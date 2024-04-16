from datetime import datetime
from pydantic import Field

from app.core.schema import VisibleBase, BaseModel


class PineconeApiInfoBase(BaseModel):
    name: str = Field(max_length=255)
    env: str = Field(max_length=255)
    key: str = Field(max_length=255)


class PineconeApiInfoCreate(PineconeApiInfoBase):
    name: str = Field(..., max_length=255)
    env: str = Field(..., max_length=255)
    key: str = Field(..., max_length=255)


class PineconeApiInfoVisible(VisibleBase):
    id: int
    name: str
    env: str
    key: str
    created_at: datetime = Field(alias="createdAt")
