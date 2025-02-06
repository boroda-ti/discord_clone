from typing import Optional, List
import datetime

from pydantic import BaseModel

class ChatReadScheme(BaseModel):

    id: int
    name: str

    class Config:
        from_attributes = True

class UserUpdateScheme(BaseModel):

    login: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_num: Optional[str] = None # TODO Think about how to change phone if i would use OTP on phone confirm
    avatar: Optional[str] = None

    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_blocked: Optional[bool] = None
    last_active: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True


class UserCreateScheme(UserUpdateScheme):

    login: str
    password: str
    phone_num: str

    is_active: bool
    is_admin: bool


class UserReadScheme(UserUpdateScheme):

    id: int

    login: str
    phone_num: str
    avatar: str

    is_active: bool
    is_admin: bool
    is_blocked: bool

    created_at: datetime.datetime
    updated_at: datetime.datetime

class UserReadWithChatsScheme(UserReadScheme):

    chats: Optional[List[ChatReadScheme]] = []

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class LoginForm(BaseModel):
    login: str
    password: str