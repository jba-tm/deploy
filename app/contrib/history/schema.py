from datetime import datetime, date
from pydantic import Field

from app.core.schema import VisibleBase, ChoiceBase
from app.contrib.history import EntityChoices, SubjectChoices


class AIHistoryVisible(VisibleBase):
    id: int
    entity: ChoiceBase[EntityChoices]
    subject_type: ChoiceBase[SubjectChoices] = Field(alias="subjectType")
    created_at: datetime = Field(alias='createdAt')


class StatisticsResult(VisibleBase):
    count: int
    statistics_date: date = Field(alias='statisticsDate')
