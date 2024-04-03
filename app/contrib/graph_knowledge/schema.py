from pydantic import Field
from app.core.schema import BaseModel


class GraphKnowledgeBase(BaseModel):
    selected_dataset = Field(alias='selectedDataset')
