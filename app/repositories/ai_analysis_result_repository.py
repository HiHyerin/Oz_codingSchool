from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_analysis_result import AiAnalysisResult


# record_id와 ai_model로 기존 AI 예측 결과를 조회하는 함수
# 역할:
# - 같은 진료기록에 같은 모델로 이미 예측한 결과가 있는지 확인한다.
async def get_ai_analysis_result_by_record_and_model(
    db: AsyncSession,
    record_id: int,
    ai_model: str,
) -> AiAnalysisResult | None:
    result = await db.execute(
        select(AiAnalysisResult).where(
            AiAnalysisResult.record_id == record_id,
            AiAnalysisResult.ai_model == ai_model,
        )
    )

    return result.scalar_one_or_none()


# AI 예측 결과를 DB에 저장하는 함수
# 역할:
# - worker 모델 예측 결과를 ai_analysis_results 테이블에 저장한다.
async def create_ai_analysis_result(
    db: AsyncSession,
    record_id: int,
    is_pneumonia: bool,
    confidence: float,
    heatmap_url: str,
    ai_model: str,
) -> AiAnalysisResult:
    result = AiAnalysisResult(
        record_id=record_id,
        is_pneumonia=is_pneumonia,
        confidence=Decimal(str(round(confidence, 2))),
        heatmap_url=heatmap_url,
        ai_model=ai_model,
    )

    db.add(result)
    await db.commit()
    await db.refresh(result)

    return result
