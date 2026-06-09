from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.medical_record import MedicalRecord
from app.models.xray_image import XrayImage


# 차트 넘버로 진료기록을 조회하는 함수
# 역할:
# - 진료기록 등록 시 chart_number 중복 여부를 확인한다.
async def get_medical_record_by_chart_number(
    db: AsyncSession,
    chart_number: str,
) -> MedicalRecord | None:
    result = await db.execute(
        select(MedicalRecord).where(MedicalRecord.chart_number == chart_number)
    )

    return result.scalar_one_or_none()


# 진료기록과 X-Ray 이미지 정보를 함께 생성하는 함수
# 역할:
# - medical_records row를 생성한다.
# - 생성된 record_id를 사용해 xray_images row를 생성한다.
# - 두 작업을 하나의 commit으로 저장한다.
async def create_medical_record_with_xray(
    db: AsyncSession,
    patient_id: int,
    chart_number: str,
    symptoms: str,
    image_url: str,
    shooting_datetime: datetime,
    uploader_id: int | None,
) -> tuple[MedicalRecord, XrayImage]:
    medical_record = MedicalRecord(
        patient_id=patient_id,
        chart_number=chart_number,
        symptoms=symptoms,
    )

    db.add(medical_record)
    await db.flush()

    xray_image = XrayImage(
        record_id=medical_record.id,
        uploader_id=uploader_id,
        image_url=image_url,
        shooting_datetime=shooting_datetime,
    )

    db.add(xray_image)
    await db.commit()
    await db.refresh(medical_record)
    await db.refresh(xray_image)

    return medical_record, xray_image
