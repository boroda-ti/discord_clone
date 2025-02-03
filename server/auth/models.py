import datetime
from typing import Optional, List

from sqlalchemy import text, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base, UserChat


class User(Base):
    __tablename__ = "user"
    __table_args__ = {
        "extend_existing": True,
    }

    id: Mapped[int] = mapped_column(primary_key = True)

    login: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(String(128)) # SHA-256 hashed password
    first_name: Mapped[Optional[str]] = mapped_column(String(30))
    last_name: Mapped[Optional[str]] = mapped_column(String(30))
    phone_num: Mapped[str] = mapped_column(String(13), unique=True) # +380671111111
    avatar: Mapped[str] = mapped_column(server_default='avatars/default.png')

    is_active: Mapped[bool] = mapped_column(server_default="false")
    is_admin: Mapped[bool] = mapped_column(server_default="false")
    is_blocked: Mapped[bool] = mapped_column(server_default="false")

    last_active: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    chats = relationship("Chat", secondary="user_chat", back_populates="users")
    messages = relationship("Message", back_populates="sender", uselist=True)

    created_at: Mapped[datetime.datetime] = mapped_column(server_default = text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime.datetime] = mapped_column(server_default = text("TIMEZONE('utc', now())"), onupdate = text("TIMEZONE('utc', now())"))


import text_chat.models