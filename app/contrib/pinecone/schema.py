import re
from datetime import datetime
from pydantic import Field, field_validator

from app.core.schema import VisibleBase, BaseModel, ChoiceBase
from app.contrib.pinecone import StatisticsTypeChoices


class PineconeApiInfoBase(BaseModel):
    name: str = Field(max_length=255)
    env: str = Field(max_length=255)
    key: str = Field(max_length=255)


class PineconeApiInfoCreate(PineconeApiInfoBase):
    name: str = Field(..., max_length=255)
    env: str = Field(..., max_length=255)
    key: str

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str):
        if len(v) != 36:
            raise ValueError('Error length of the API Key.')
        if not re.match(r'^[0-9a-fA-F-]+$', v):
            raise ValueError('API Key includes invalid character.')
        return v


class PineconeApiInfoVisible(VisibleBase):
    id: int
    name: str
    env: str
    key: str
    created_at: datetime = Field(alias="createdAt")


class FileInfoVisible(VisibleBase):
    id: int
    file: str
    file_name: str = Field(alias="fileName")
    created_at: datetime = Field(alias="createdAt")
    pinecone: PineconeApiInfoVisible
    status: ChoiceBase[StatisticsTypeChoices]
