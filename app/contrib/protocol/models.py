from sqlalchemy import Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.models import UUIDBase,CreationModificationDateBase


class Protocol(UUIDBase, CreationModificationDateBase):
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    step: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
