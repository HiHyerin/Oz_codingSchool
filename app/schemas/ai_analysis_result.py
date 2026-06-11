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


# 역할:
# - 어떤 AI 모델로 예측할지 요청 body에서 받는다.
# - 값이 없으면 기본 모델 SimpleCNN-v1을 사용한다.
class AiPneumoniaPredictionRequest(BaseModel):
    ai_model: str = "SimpleCNN-v1"


class AiPneumoniaPredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # AI 예측 결과 고유 ID
    id: int

    # 진료기록 ID
    record_id: int

    # 폐렴 여부
    is_pneumonia: bool

    # 예측 라벨
    # NORMAL 또는 PNEUMONIA
    prediction_label: str

    # 예측 라벨에 대한 confidence
    confidence: float

    # 정상 확률
    normal_probability: float

    # 폐렴 확률
    pneumonia_probability: float

    # Heatmap 이미지 URL
    # 아직 heatmap을 만들지 않으면 None 허용
    heatmap_url: str | None = None

    # 사용한 AI 모델명
    ai_model: str

    # 기존 저장 결과를 재사용했는지 여부
    is_cached: bool

    # 생성일시
    created_at: datetime

    # 수정일시
    updated_at: datetime | None = None
