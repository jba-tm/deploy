from uuid import UUID
from sqlalchemy import Text, String, ForeignKey, UniqueConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as SUUID
from sqlalchemy_utils import ChoiceType

from app.db.models import UUIDBase, CreationModificationDateBase
from app.contrib.protocol import ProtocolSourceChoices


class Protocol(UUIDBase, CreationModificationDateBase):
    user_id: Mapped[UUID] = mapped_column(
        SUUID(as_uuid=True),
        ForeignKey("user.id", name='fx_protocol_user_id', ondelete="CASCADE"),
        nullable=False,
    )
    current_step: Mapped[str] = mapped_column(String(), nullable=True)
    medicine: Mapped[str] = mapped_column(String(), nullable=False)


class ProtocolStep(CreationModificationDateBase):
    user_id: Mapped[UUID] = mapped_column(
        SUUID(as_uuid=True),
        ForeignKey("user.id", name='fx_protocol_step_user_id', ondelete="CASCADE"),
        nullable=False,
    )
    protocol_id: Mapped[UUID] = mapped_column(
        SUUID(as_uuid=True),
        ForeignKey(
            "protocol.id", name="fx_p_step_protocol_id", ondelete="CASCADE"
        )
    )
    question: Mapped[str] = mapped_column(Text(), nullable=False)
    prompt: Mapped[str] = mapped_column(Text(), nullable=False)
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    source: Mapped[ProtocolSourceChoices] = mapped_column(
        ChoiceType(choices=ProtocolSourceChoices, impl=String(25)), nullable=False
    )
    step: Mapped[str] = mapped_column(String(50), nullable=False)
    step_order: Mapped[int] = mapped_column(Integer(), nullable=False)
    protocol = relationship("Protocol",  lazy="noload")

    __table_args__ = (
        UniqueConstraint('protocol_id', 'step', name='ux_protocol_id_step'),
    )
