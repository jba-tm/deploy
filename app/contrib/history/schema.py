from datetime import datetime, date
from pydantic import Field

from app.core.schema import VisibleBase, ChoiceBase


class AIHistoryVisible(VisibleBase):
    id: int
    entity: ChoiceBase
    subject_type: ChoiceBase = Field(alias="subjectType")
    created_at: datetime = Field(alias='createdAt')


class StatisticsResult(VisibleBase):
    count: int
    statistics_date: date = Field(alias='statisticsDate')
