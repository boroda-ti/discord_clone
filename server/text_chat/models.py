from typing import List
from enum import Enum
import datetime

from sqlalchemy import ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base, UserChat
from auth.models import User


class DataTypeEnum(Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    FILE = "FILE"


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(Text)

    users: Mapped[List["User"]] = relationship(secondary="user_chat", back_populates="chats")
    messages: Mapped[List["Message"]] = relationship(back_populates="chat")

    created_at: Mapped[datetime.datetime] = mapped_column(server_default = text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime.datetime] = mapped_column(server_default = text("TIMEZONE('utc', now())"), onupdate = text("TIMEZONE('utc', now())"))


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)

    data: Mapped[str] = mapped_column(Text)
    data_type: Mapped[DataTypeEnum]

    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))

    sender: Mapped["User"] = relationship("User", back_populates="messages", uselist=False)
    chat: Mapped["Chat"] = relationship("Chat",  back_populates="messages", uselist=False)

    created_at: Mapped[datetime.datetime] = mapped_column(server_default = text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime.datetime] = mapped_column(server_default = text("TIMEZONE('utc', now())"), onupdate = text("TIMEZONE('utc', now())"))