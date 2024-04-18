from uuid import UUID
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models import CreationModificationDateBase


class FileInfo(CreationModificationDateBase):
    user_id: Mapped[UUID] = mapped_column(
        SUUID(as_uuid=True),
        ForeignKey('user.id', ondelete="CASCADE", name="fx_file_info_user_id"),
        nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file: Mapped[str] = mapped_column(Text(), nullable=False)


class PineconeApiInfo(CreationModificationDateBase):
    user_id: Mapped[UUID] = mapped_column(
        SUUID(as_uuid=True),
        ForeignKey('user.id', ondelete="CASCADE", name="fx_pai_user_id"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    env: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
