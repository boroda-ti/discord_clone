from typing import List, Optional
from jose import JWTError

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query, Path
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import database

from auth.router import oauth2_scheme
from auth.service import user_auth
from auth.models import User

from text_chat.service import ChatSocketManager
from text_chat.models import Chat, Message
from text_chat.schema import ChatReadScheme, ChatCreateScheme, ChatUpdateScheme

ws_router = APIRouter()

socket_manager = ChatSocketManager()

@ws_router.websocket("/chat")
async def chat_websocket(websocket: WebSocket):

    # 1. Accept websocket
    # 2. Get user_id from first message
    # 3. Get user's all chat_id
    # 4. While true manage communication


    await websocket.accept()

    auth_data = await websocket.receive_json()
    user_id = auth_data.get("user_id")

    chat_ids = [0, 1]

    await socket_manager.connect(websocket, user_id, chat_ids)

    try:
        while True:
            data = await websocket.receive_json()
            chat_id = data.get("chat_id")
            for client in socket_manager.active_connections:
                if client != user_id and chat_id in socket_manager.active_connections[client][1]:
                    await socket_manager.active_connections[client][0].send_json(data)

    except WebSocketDisconnect as e:
        # LOG disconnect
        print(e)
        print("Client disconnected")





api_router = APIRouter()

# 1. Create, Read, Update, Delete chats
# 2. Create, Read, Delete (One, All) messages

@api_router.delete("/remove/{login}/{chat_id}")
async def delete_user_from_chat(login: str = Path(...), chat_id: int = Path(...), token: str = Depends(oauth2_scheme)):
    try:
        admin_login = user_auth.decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    admin = await user_auth.get_user(admin_login)
    if not admin:
        raise HTTPException(status_code=404, detail="User not found")
    elif not admin.is_admin:
        raise HTTPException(status_code=403, detail="User does not have admin permissions")
    
    async with database.async_session() as session:
        user = await user_auth.get_user_with_chats(login)
        user = await session.merge(user)

        try:
            chat = (await session.execute(
                select(Chat)
                .where(Chat.id == chat_id)
            )).scalars().first()
        except Exception as e:
            raise HTTPException(status_code=404, detail="Chat not found")

        try:
            user.chats.remove(chat)
            await session.commit()
        except Exception as e:
            raise HTTPException(status_code=404, detail="User not in the chat")

    return {"message": "User deleted from chat successfully"}

@api_router.post("/add/{login}/{chat_id}")
async def add_user_from_chat(login: str = Path(...), chat_id: int = Path(...), token: str = Depends(oauth2_scheme)):
    try:
        request_login = user_auth.decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    user = await user_auth.get_user_with_chats(request_login)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.chats and not user.is_admin:
        raise HTTPException(status_code=404, detail="User do not have any chats")

    async with database.async_session() as session:
        if user.is_admin:
            query = select(Chat).where(Chat.id == chat_id)
        else:
            query = select(Chat).where((Chat.id.in_([chat.id for chat in user.chats])) & (Chat.id == chat_id))

        result = await session.execute(query.options(selectinload(Chat.users)))
        chat = result.scalars().first()

        if chat is None:
            raise HTTPException(status_code=404, detail="User not in the chat")

        result = await session.execute(select(User).where(User.login == login))
        new_user = result.scalars().first()

        if new_user is None:
            raise HTTPException(status_code=404, detail="User with this login not found")

        if new_user not in chat.users:
            chat.users.append(new_user)

        await session.commit()
        await session.refresh(chat)
        
    return ChatReadScheme.model_validate({
                **chat.__dict__,
                "users": [user.id for user in chat.users]
            })

@api_router.get("/my")
async def get_user_chats(token: str = Depends(oauth2_scheme)) -> Optional[List[ChatReadScheme]]:
    try:
        login = user_auth.decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    user = await user_auth.get_user_with_chats(login)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.chats:
        return []

    async with database.async_session() as session:
        result = await session.execute(
            select(Chat)
            .where(Chat.id.in_([chat.id for chat in user.chats]))
            .options(selectinload(Chat.users))
        )
        chats = result.scalars().all()
        
    return [ChatReadScheme.model_validate({
                **chat.__dict__,
                "users": [user.id for user in chat.users]
            }) for chat in chats
        ]
    
@api_router.get("/get/{chat_id}")
async def get_chat(chat_id: int = Path(...), token: str = Depends(oauth2_scheme)) -> Optional[ChatReadScheme]:
    try:
        login = user_auth.decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    user = await user_auth.get_user_with_chats(login)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.chats and not user.is_admin:
        raise HTTPException(status_code=404, detail="User do not have any chats")

    async with database.async_session() as session:
        if user.is_admin:
            query = select(Chat).where(Chat.id == chat_id)
        else:
            query = select(Chat).where((Chat.id.in_([chat.id for chat in user.chats])) & (Chat.id == chat_id))

        result = await session.execute(query.options(selectinload(Chat.users)))
        chat = result.scalars().first()

    if chat is None:
        raise HTTPException(status_code=404, detail="User not in the chat")
        
    return ChatReadScheme.model_validate({
                **chat.__dict__,
                "users": [user.id for user in chat.users]
            })

@api_router.post("/create")
async def create_chat(data: ChatCreateScheme, token: str = Depends(oauth2_scheme)) -> ChatReadScheme:
    try:
        login = user_auth.decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    user = await user_auth.get_user(login)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    async with database.async_session() as session:

        users = await session.execute(select(User).where(User.id.in_([user.id] + data.users)))
        users = users.scalars().all()

        if not users:
            raise HTTPException(status_code=400, detail="Invalid users")

        chat_new = Chat(
            name = data.name,
            users = users
        )
   
        session.add(chat_new)

        try:
            await session.commit()
            await session.refresh(chat_new)
        except Exception as e:
            print(f"LOGGER: ERRROR \n\n{e}\n\n")# LOG the error
            await session.rollback()
            raise HTTPException(status_code=400, detail="Error creating chat")
        
    return ChatReadScheme.model_validate({
        **chat_new.__dict__,
        "users": [user.id for user in chat_new.users]
    })


@api_router.patch("/update/{chat_id}")
async def update_chat(data: ChatUpdateScheme, chat_id: int = Path(...), token: str = Depends(oauth2_scheme)) -> Optional[ChatReadScheme]:
    try:
        login = user_auth.decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    user = await user_auth.get_user_with_chats(login)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.chats and not user.is_admin:
        raise HTTPException(status_code=404, detail="User do not have any chats")

    async with database.async_session() as session:
        if user.is_admin:
            query = select(Chat).where(Chat.id == chat_id)
        else:
            query = select(Chat).where((Chat.id.in_([chat.id for chat in user.chats])) & (Chat.id == chat_id))

        result = await session.execute(query.options(selectinload(Chat.users)))
        chat = result.scalars().first()

        if chat is None:
            raise HTTPException(status_code=404, detail="User not in the chat")

        for key, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
            if key == "users":
                result = await session.execute(
                    select(User).where(User.id.in_(value))
                )
                users = result.scalars().all()
                for user in users:
                    if user not in chat.users:
                        chat.users.append(user)
            else:
                setattr(chat, key, value)

        await session.commit()
        await session.refresh(chat)

    return ChatReadScheme.model_validate({
        **chat.__dict__,
        "users": [user.id for user in chat.users]
    })