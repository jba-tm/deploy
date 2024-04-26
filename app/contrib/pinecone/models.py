from uuid import UUID
from sqlalchemy import String, Text, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID as SUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import ChoiceType
from app.db.models import CreationModificationDateBase
from app.contrib.pinecone import FileInfoStatusChoices


class FileInfo(CreationModificationDateBase):
    user_id: Mapped[UUID] = mapped_column(
        SUUID(as_uuid=True),
        ForeignKey('user.id', ondelete="CASCADE", name="fx_file_info_user_id"),
        nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file: Mapped[str] = mapped_column(Text(), nullable=False)

    pinecone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pinecone_api_info.id", name='fx_file_info_pai_id', ondelete="RESTRICT"),
        nullable=False
    )
    status: Mapped[bool] = mapped_column(ChoiceType(
        choices=FileInfoStatusChoices, impl=String(25)
    ), nullable=False, default=FileInfoStatusChoices.PENDING)
    pinecone = relationship("PineconeApiInfo", lazy="noload")


class PineconeApiInfo(CreationModificationDateBase):
    user_id: Mapped[UUID] = mapped_column(
        SUUID(as_uuid=True),
        ForeignKey('user.id', ondelete="CASCADE", name="fx_pai_user_id"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    env: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
