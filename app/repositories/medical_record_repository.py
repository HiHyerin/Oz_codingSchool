from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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


# 특정 환자의 진료기록 목록을 조회하는 함수
# 역할:
# - patient_id에 해당하는 진료기록만 조회한다.
# - page, size 값으로 페이지네이션을 처리한다.
async def get_medical_record_list_by_patient_id(
    db: AsyncSession,
    patient_id: int,
    page: int = 1,
    size: int = 20,
) -> list[MedicalRecord]:
    query = (
        select(MedicalRecord)
        .where(MedicalRecord.patient_id == patient_id)
        .order_by(MedicalRecord.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    )

    result = await db.execute(query)

    return list(result.scalars().all())


# 특정 환자의 진료기록 전체 개수를 조회하는 함수
# 역할:
# - 진료기록 목록 조회 응답의 total 값을 계산한다.
async def count_medical_record_list_by_patient_id(
    db: AsyncSession,
    patient_id: int,
) -> int:
    result = await db.execute(
        select(func.count(MedicalRecord.id)).where(
            MedicalRecord.patient_id == patient_id
        )
    )

    return result.scalar_one()


# 진료기록 상세 정보를 조회하는 함수
# 역할:
# - record_id와 patient_id가 모두 일치하는 진료기록을 조회한다.
# - 상세 응답에 필요한 X-Ray 이미지 목록을 함께 로딩한다.
async def get_medical_record_detail(
    db: AsyncSession,
    patient_id: int,
    record_id: int,
) -> MedicalRecord | None:
    result = await db.execute(
        select(MedicalRecord)
        .options(selectinload(MedicalRecord.xray_images))
        .where(
            MedicalRecord.id == record_id,
            MedicalRecord.patient_id == patient_id,
        )
    )

    return result.scalar_one_or_none()
