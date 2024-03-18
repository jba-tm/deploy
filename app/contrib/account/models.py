from typing import Optional
from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy_utils import ChoiceType
from sqlalchemy.dialects.postgresql import UUID as SUUID

from app.db.models import UUIDBase, CreationModificationDateBase, Base
from app.contrib.account import GenderChoices


class User(UUIDBase, CreationModificationDateBase):
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[Optional[GenderChoices]] = mapped_column(
        ChoiceType(choices=GenderChoices, impl=String(25)), nullable=True, default=None
    )
    birthday: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    signature: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)


class FileInfo(CreationModificationDateBase):
    user_id: Mapped[UUID] = mapped_column(
        SUUID(as_uuid=True),
        ForeignKey('user.id', ondelete="CASCADE", name="fx_file_info_user_id"),
        nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file: Mapped[str] = mapped_column(Text(), nullable=False)


class PineconeApiInfo(Base):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    env: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
