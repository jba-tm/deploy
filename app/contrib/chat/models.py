from uuid import UUID
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as SUUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.models import UUIDBase, CreationModificationDateBase


class Chat(UUIDBase, CreationModificationDateBase):
    user_id: Mapped[UUID] = mapped_column(SUUID, ForeignKey("user.id", name="fx_chat_user_id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)


class ChatItem(CreationModificationDateBase):
    body: Mapped[dict] = mapped_column(JSON, default={}, nullable=False)
    answer: Mapped[dict] = mapped_column(JSON, default={}, nullable=False)
    chat_id: Mapped[UUID] = mapped_column(
        SUUID(as_uuid=True),
        ForeignKey("chat.id", name="fx_chat_item_chat_id", ondelete="CASCADE"),
        nullable=False
    )


class ChatFavorite(UUIDBase, CreationModificationDateBase):
    question: Mapped[str] = mapped_column(String(255), nullable=False)
    answer: Mapped[str] = mapped_column(Text(), nullable=False)
