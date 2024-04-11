from uuid import UUID
from sqlalchemy import Text, JSON, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import ChoiceType
from sqlalchemy.dialects.postgresql import UUID as SUUID

from app.db.models import CreationModificationDateBase
from app.contrib.history import EntityChoices, SubjectChoices


class AIHistory(CreationModificationDateBase):
    user_id: Mapped[UUID] = mapped_column(
        SUUID(as_uuid=True),
        ForeignKey('user.id', ondelete="CASCADE", name="fx_ai_history_user_id"),
        nullable=False
    )
    entity: Mapped[EntityChoices] = mapped_column(
        ChoiceType(choices=EntityChoices, impl=String(50)),
        nullable=False
    )
    subject_type: Mapped[SubjectChoices] = mapped_column(
        ChoiceType(choices=SubjectChoices, impl=String(50)),
        nullable=False
    )
    content: Mapped[dict] = mapped_column(JSON, nullable=True)
