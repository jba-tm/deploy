from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import Field
from app.core.schema import BaseModel, VisibleBase, ChoiceBase
from app.contrib.protocol import ProtocolSourceChoices


class ProtocolStepBase(BaseModel):
    question: str = Field(alias="question")
    content: str = Field(alias="content")


class ProtocolStepCreate(BaseModel):
    medicine: str = Field(max_length=255)
    step: str = Field(..., alias="step")
    step_order: int = Field(..., alias="stepOrder")

    protocol_id: UUID = Field(..., alias="protocolId")


class ProtocolStepVisible(VisibleBase):
    id: int
    question: str
    prompt: str
    content: str
    source: ChoiceBase
    step: str
    step_order: int = Field(alias="stepOrder")
    created_at: datetime = Field(alias="createdAt")


class ProtocolBase(BaseModel):
    medicine: str = Field(max_length=255)


class ProtocolCreate(ProtocolBase):
    medicine: str = Field(..., max_length=255)


class ProtocolVisible(VisibleBase):
    id: UUID
    medicine: str
    current_step: str = Field(alias="currentStep")

    created_at: datetime = Field(alias="createdAt")


class ProtocolExtended(ProtocolVisible):
    current_step_obj: ProtocolStepVisible = Field(alias="currentStepObj")


class ProtocolSource(BaseModel):
    source_type: ProtocolSourceChoices = Field(alias="sourceType")
    query: str
