from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.xray_image import XrayImage


# record_id로 X-Ray 이미지 1개를 조회하는 함수
# 역할:
# - AI 예측에 사용할 진료기록의 X-Ray 이미지를 가져온다.
# - 여러 장이 있을 경우 가장 먼저 등록된 이미지를 사용한다.
async def get_first_xray_image_by_record_id(
    db: AsyncSession,
    record_id: int,
) -> XrayImage | None:
    result = await db.execute(
        select(XrayImage)
        .where(XrayImage.record_id == record_id)
        .order_by(XrayImage.id.asc())
        .limit(1)
    )

    return result.scalar_one_or_none()
