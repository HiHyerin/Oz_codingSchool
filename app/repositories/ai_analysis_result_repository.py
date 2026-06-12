from decimal import Decimal

from sqlalchemy import func, select
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


# record_id로 AI 예측 결과 목록을 조회하는 함수
# 역할:
# - 특정 진료기록에 저장된 AI 예측 결과를 페이지네이션하여 조회한다.
async def get_ai_analysis_result_list_by_record_id(
    db: AsyncSession,
    record_id: int,
    page: int = 1,
    size: int = 20,
) -> list[AiAnalysisResult]:
    query = (
        select(AiAnalysisResult)
        .where(AiAnalysisResult.record_id == record_id)
        .order_by(AiAnalysisResult.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    )

    result = await db.execute(query)

    return list(result.scalars().all())


# record_id로 AI 예측 결과 전체 개수를 조회하는 함수
# 역할:
# - AI 예측 결과 목록 조회 응답의 total 값을 계산한다.
async def count_ai_analysis_result_list_by_record_id(
    db: AsyncSession,
    record_id: int,
) -> int:
    result = await db.execute(
        select(func.count(AiAnalysisResult.id)).where(
            AiAnalysisResult.record_id == record_id
        )
    )

    return result.scalar_one()


# analysis_id와 record_id로 AI 예측 결과를 조회하는 함수
# 역할:
# - 특정 진료기록에 속한 특정 AI 예측 결과를 조회한다.
# - analysis_id만으로 조회하지 않고 record_id도 함께 확인해서 다른 진료기록 결과 접근을 막는다.
async def get_ai_analysis_result_detail(
    db: AsyncSession,
    record_id: int,
    analysis_id: int,
) -> AiAnalysisResult | None:
    result = await db.execute(
        select(AiAnalysisResult).where(
            AiAnalysisResult.id == analysis_id,
            AiAnalysisResult.record_id == record_id,
        )
    )

    return result.scalar_one_or_none()
