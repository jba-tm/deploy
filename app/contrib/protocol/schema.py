from uuid import UUID

from pydantic import Field
from app.core.schema import BaseModel, VisibleBase


class ProtocolBase(BaseModel):
    content: str = Field(max_length=1000)
    step: int = Field(gte=0)


class ProtocolCreate(ProtocolBase):
    content: str = Field(..., max_length=1000)
    step: int = Field(..., gte=0)


class ProtocolVisible(VisibleBase):
    id: UUID
    content: str
    step: int
