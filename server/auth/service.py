from jose import jwt
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import database
from config import BaseConfig

from auth.models import User
from auth.utils import hash_password


class UserAuth:

    def create_access_token(self, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, BaseConfig.get("JWT_SECRET_KEY"), algorithm=BaseConfig.get("JWT_ALGORITHM"))

    def create_refresh_token(self, login: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=int(BaseConfig.get("JWT_REFRESH_TOKEN_EXPIRE_DAYS")))
        to_encode = {"sub": login, "exp": expire}

        return jwt.encode(to_encode, BaseConfig.get("JWT_SECRET_KEY"), algorithm=BaseConfig.get("JWT_ALGORITHM"))
    
    def decode_token(self, token: str) -> str:
        payload = jwt.decode(token, BaseConfig.get("JWT_SECRET_KEY"), algorithms=[BaseConfig.get("JWT_ALGORITHM")])
        login = payload.get('sub')
        return login

    def verify_password(self, plain_login: str, plain_password: str, hashed_password: str):
        return hash_password(plain_login, plain_password) == hashed_password

    async def get_user(self, login: str):
        async with database.async_session() as session:
            result = await session.execute(
                select(User).where(User.login == login)
            )
            user = result.scalars().first()
        
        return user
    
    async def get_user_with_chats(self, login: str) -> User:
        async with database.async_session() as session:
            result = await session.execute(
                select(User).where(User.login == login).options(selectinload(User.chats))
            )
            user = result.scalars().first()
        
        return user
    
user_auth = UserAuth()