from datetime import datetime
from pydantic import Field

from app.core.schema import VisibleBase
from app.contrib.history import EntityChoices, SubjectChoices


class AIHistoryVisible(VisibleBase):
    id: int
    entity: EntityChoices
    subject_type: SubjectChoices = Field(alias="subjectType")
    created_at: datetime = Field(alias='createdAt')
