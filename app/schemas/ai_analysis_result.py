from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AiAnalysisResultBase(BaseModel):
    record_id: int
    is_pneumonia: bool
    confidence: Decimal
    heatmap_url: str
    ai_model: str


class AiAnalysisResultCreate(AiAnalysisResultBase):
    pass


class AiAnalysisResultUpdate(BaseModel):
    record_id: int | None = None
    is_pneumonia: bool | None = None
    confidence: Decimal | None = None
    heatmap_url: str | None = None
    ai_model: str | None = None


class AiAnalysisResultRead(AiAnalysisResultBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime | None = None
