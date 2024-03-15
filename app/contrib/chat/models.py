from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.models import UUIDBase, CreationModificationDateBase


class ChatHistory(UUIDBase, CreationModificationDateBase):
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    chat_data: Mapped[dict] = mapped_column(JSON, default={}, nullable=False)


class ChatFavorite(UUIDBase, CreationModificationDateBase):
    question: Mapped[str] = mapped_column(String(255), nullable=False)
    answer: Mapped[str] = mapped_column(Text(), nullable=False)
