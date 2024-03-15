from uuid import UUID

from pydantic import Field
from app.core.schema import BaseModel, VisibleBase


class ChatHistoryBase(BaseModel):
    title: str = Field(max_length=255)
    chat_data: dict = Field({}, alias="chatData")


class ChatHistoryCreate(ChatHistoryBase):
    title: str = Field(..., max_length=255)


class ChatVisible(VisibleBase):
    id: UUID
    title: str
    chat_data: dict = Field(alias="chatData")


class ChatFavoriteBase(BaseModel):
    question: str = Field(max_length=255)
    answer: str = Field(max_length=500)


class ChatFavoriteCreate(ChatFavoriteBase):
    question: str = Field(..., max_length=255)
    answer: str = Field(..., max_length=500)


class ChatFavoriteVisible(VisibleBase):
    id: UUID
    question: str
    answer: str
