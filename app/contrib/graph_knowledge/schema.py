from typing import List
from pydantic import Field
from app.core.schema import BaseModel
from app.contrib.graph_knowledge import DrugFilterChoices, ClinicTrialFilterChoices


class GraphKnowledgeMedicineBase(BaseModel):
    search: str = Field(..., max_length=255)
    filters: List[DrugFilterChoices] = Field(default_factory=list, alias="filters")


class GraphKnowledgeClinicalTrialsBase(BaseModel):
    search: str = Field(..., max_length=255)
    filters: List[ClinicTrialFilterChoices] = Field(default_factory=list, alias="filters")
