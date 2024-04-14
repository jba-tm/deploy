from uuid import UUID
from sqlalchemy import String, Text, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID as SUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models import UUIDBase, CreationModificationDateBase


class Chat(UUIDBase, CreationModificationDateBase):
    is_favorite: Mapped[bool] = mapped_column(Boolean(), default=False)
    user_id: Mapped[UUID] = mapped_column(
        SUUID(as_uuid=True),
        ForeignKey("user.id", name="fx_chat_user_id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)


class ChatItem(CreationModificationDateBase):
    chat_id: Mapped[UUID] = mapped_column(
        SUUID(as_uuid=True),
        ForeignKey(
            "chat.id",
            name="fx_chat_item_chat_id",
            ondelete="CASCADE",
        ),
        nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        SUUID(as_uuid=True),
        ForeignKey("user.id", name="fx_chat_item_user_id", ondelete="CASCADE"), nullable=False
    )

    body = relationship("ChatItemBody", lazy="noload")
    chat = relationship("Chat", lazy="noload")


class ChatItemBody(CreationModificationDateBase):
    item_id: Mapped[int] = mapped_column(
        Integer(), ForeignKey(
            'chat_item.id',
            ondelete='CASCADE',
            name='fx_ch_body_chat_item_id'
        ),
        nullable=False,
        unique=False,
    )
    body: Mapped[str] = mapped_column(Text(), nullable=False)
    answers = relationship("ChatItemAnswer", lazy="noload")


class ChatItemAnswer(CreationModificationDateBase):
    body_id: Mapped[int] = mapped_column(
        Integer(), ForeignKey(
            'chat_item_body.id',
            ondelete='CASCADE',
            name='fx_cha_cib_id'
        ),
        nullable=False,
        unique=False,
    )
    answer: Mapped[str] = mapped_column(Text(), nullable=False)
