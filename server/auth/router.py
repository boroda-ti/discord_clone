from typing import Optional
from jose import jwt, JWTError
from datetime import timedelta

from fastapi import APIRouter, Query, HTTPException, Depends, Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from server.database import database
from server.config import BaseConfig

from auth.models import User
from auth.schema import UserReadScheme, UserReadWithChatsScheme, UserCreateScheme, UserUpdateScheme, Token, LoginForm
from auth.utils import hash_password
from auth.service import user_auth


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()


@router.post("/signup")
async def create_user(user: UserCreateScheme = None) -> Optional[UserReadScheme]:
    async with database.async_session() as session:
        existing_user = await session.execute(
            select(User).where((User.login == user.login) | (User.phone_num == user.phone_num))
        )

        if existing_user.scalar():
            raise HTTPException(status_code=400, detail="User with this login or phone number already exists")

        new_user = User(
            login = user.login,
            password = hash_password(user.login, user.password),
            first_name = user.first_name,
            last_name = user.last_name,
            phone_num = user.phone_num,
            avatar = user.avatar or 'avatars/default.png',
            is_active = False,
            is_admin = user.is_admin
        )

        session.add(new_user)
        try:
            await session.commit()
            await session.refresh(new_user, ["chats"])
        except Exception as e:
            print(f"LOGGER: ERRROR \n\n{e}\n\n")# LOG the error
            await session.rollback()
            raise HTTPException(status_code=400, detail="Error creating user")

        return UserReadScheme.model_validate(new_user)
    

# TODO
# 1. Create route sign in. Singin is get token endpoint!!! DONE
# 2. Create route for searching by login or phone DONE
# 3. Create logic for user logger for admins
# 4. Create remove user from chat DONE

@router.get("/me")
async def get_me(token: str = Depends(oauth2_scheme)) -> Optional[UserReadWithChatsScheme]:
    try:
        login = user_auth.decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    user = await user_auth.get_user_with_chats(login)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserReadWithChatsScheme.model_validate(user)

@router.get("/user/get")
async def get_user(login: Optional[str] = Query(None), phone: Optional[str] = Query(None), token: str = Depends(oauth2_scheme)) -> Optional[UserReadWithChatsScheme]:
    try:
        request_login = user_auth.decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    request_user = await user_auth.get_user(request_login)
    if not request_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not login and not phone:
        raise HTTPException(status_code=400, detail="Either login or phone must be provided")

    async with database.async_session() as session:
        query = select(User).where((User.login == login) | (User.phone_num == f"+{phone}"))
        
        if request_user.is_admin:
            query = query.options(selectinload(User.chats))
        
        result = await session.execute(query)
        user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if request_user.is_admin:
        return UserReadWithChatsScheme.model_validate(user)
    else:
        return UserReadScheme.model_validate(user)


@router.patch("/me/update")
async def update_me(data: UserUpdateScheme, token: str = Depends(oauth2_scheme)) -> Optional[UserReadScheme]:
    try:
        login = user_auth.decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    user = await user_auth.get_user_with_chats(login)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    async with database.async_session() as session:
        user = await session.merge(user)

        for key, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
            if key in ["is_admin", "is_active", "last_active", "is_blocked"]:
                continue
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)

    return UserReadScheme.model_validate(user)
    

@router.patch("/user/update/{login}")
async def update_user(login: str = Path(...), data: UserUpdateScheme = None, token: str = Depends(oauth2_scheme)) -> Optional[UserReadScheme]:
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
        user = await user_auth.get_user(login)
        user = await session.merge(user)

        for key, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(user, key, value)

        try:
            await session.commit()
            await session.refresh(user)
        except IntegrityError:
            raise HTTPException(status_code=404, detail="User with this login or phone already exist")

    return UserReadScheme.model_validate(user)
    

@router.delete("/me/delete")
async def delete_me(token: str = Depends(oauth2_scheme)):
    try:
        login = user_auth.decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    user = await user_auth.get_user_with_chats(login)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    async with database.async_session() as session:
        user = await session.merge(user)
        await session.delete(user)
        await session.commit()

    return {"message": "User deleted successfully"}


@router.delete("/user/delete/{login}")
async def delete_user(login: str = Path(...), token: str = Depends(oauth2_scheme)):
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
        user = await user_auth.get_user(login)
        user = await session.merge(user)
        
        await session.delete(user)
        await session.commit()

    return {"message": "User deleted successfully"}



# JWT
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: LoginForm) -> Token:
    user = await user_auth.get_user(form_data.login)
    if not user or not user_auth.verify_password(form_data.login, form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = user_auth.create_access_token({"sub": form_data.login}, timedelta(minutes=int(BaseConfig.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))))
    refresh_token = user_auth.create_refresh_token(form_data.login)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/token/refresh")
def refresh_token(refresh_token: str) -> dict:
    try:
        payload = jwt.decode(refresh_token, BaseConfig.get("JWT_SECRET_KEY"), algorithms=[BaseConfig.get("JWT_ALGORITHM")])
        login = payload.get("sub")
        if login is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_access_token = user_auth.create_access_token({"sub": login}, timedelta(minutes=int(BaseConfig.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))))
        return {"access_token": new_access_token}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")