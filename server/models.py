import datetime

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserChat(Base):
    __tablename__ = "user_chat"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id", ondelete="CASCADE"), primary_key=True)

    is_pinned: Mapped[bool] = mapped_column(server_default="false")
    joined_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))