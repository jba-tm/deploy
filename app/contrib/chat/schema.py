from typing import Sequence
from uuid import UUID
from datetime import datetime
from pydantic import Field
from typing_extensions import Annotated
from app.core.schema import BaseModel, VisibleBase


class ChatItemBase(BaseModel):
    body: str = Field(max_length=2500)


class ChatItemCreate(BaseModel):
    body: str = Field(..., max_length=2500)


class ChatItemAnswer(BaseModel):
    id: int
    answer: str
    created_at: datetime = Field(alias="createdAt")


class ChatItemBody(BaseModel):
    id: int
    body: str
    answers: Sequence[ChatItemAnswer] = Field(default_factory=list)
    created_at: datetime = Field(alias="createdAt")


class ChatItemVisible(VisibleBase):
    id: int
    body: Annotated[Sequence[ChatItemBody], Field(..., default_factory=list)]
    created_at: datetime = Field(alias="createdAt")


class ChatBase(BaseModel):
    title: str = Field(max_length=255)


class ChatCreate(ChatBase):
    title: str = Field(..., max_length=255)


class ChatVisible(VisibleBase):
    id: UUID
    title: str
    created_at: datetime = Field(alias="createdAt")
    items: Sequence[ChatItemVisible] = Field(default_factory=list)


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
