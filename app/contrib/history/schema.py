from datetime import datetime, date
from pydantic import Field

from app.core.schema import VisibleBase
from app.contrib.history import EntityChoices, SubjectChoices


class AIHistoryVisible(VisibleBase):
    id: int
    entity: EntityChoices
    subject_type: SubjectChoices = Field(alias="subjectType")
    created_at: datetime = Field(alias='createdAt')


class StatisticsResult(VisibleBase):
    count: int
    statistics_date: date = Field(alias='statisticsDate')
