from typing import Optional, List
import datetime

from pydantic import BaseModel

class ChatUpdateScheme(BaseModel):

    name: Optional[str] = None

    users: Optional[List[int]] = None
    #messages: Optional[List[int]] = None

    class Config:
        from_attributes = True

class ChatReadScheme(ChatUpdateScheme):

    id: int
    name: str

    users: List[int] = None

    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None

class ChatCreateScheme(ChatUpdateScheme):
    name: str

    users: List[int] = None

    # created_at: datetime.datetime = None
    # updated_at: datetime.datetime = None