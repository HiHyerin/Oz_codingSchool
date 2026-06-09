from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.medical_record_repository import (
    count_medical_record_list_by_patient_id,
    create_medical_record_with_xray,
    get_medical_record_by_chart_number,
    get_medical_record_detail,
    get_medical_record_list_by_patient_id,
)
from app.repositories.patient_repository import get_patient_by_id


BASE_DIR = Path(__file__).resolve().parent.parent.parent
XRAY_UPLOAD_DIR = BASE_DIR / "media" / "xray"


# 업로드된 X-Ray 이미지 파일을 로컬 저장소에 저장하는 함수
# 역할:
# - 이미지 파일인지 검증한다.
# - 파일명을 UUID 기반으로 안전하게 만든다.
# - 저장된 파일의 URL 경로를 반환한다.
async def save_xray_image_file(xray_image: UploadFile) -> str:
    if not xray_image.content_type or not xray_image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지 파일만 업로드할 수 있습니다.",
        )

    original_name = Path(xray_image.filename or "xray_image").name
    suffix = Path(original_name).suffix
    saved_name = f"{uuid4().hex}{suffix}"

    XRAY_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = XRAY_UPLOAD_DIR / saved_name

    file_content = await xray_image.read()

    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="업로드된 이미지 파일이 비어 있습니다.",
        )

    saved_path.write_bytes(file_content)

    return f"/media/xray/{saved_name}"


# 진료기록 등록 비즈니스 로직 함수
# 역할:
# - 환자 존재 여부를 확인한다.
# - chart_number 중복 여부를 확인한다.
# - X-Ray 이미지 파일을 로컬 저장소에 저장한다.
# - 진료기록과 X-Ray 이미지 DB row를 생성한다.
async def register_medical_record(
    db: AsyncSession,
    patient_id: int,
    chart_number: str,
    symptoms: str,
    shooting_datetime: datetime,
    xray_image: UploadFile,
    current_user: User,
):
    patient = await get_patient_by_id(db, patient_id)

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="환자를 찾을 수 없습니다.",
        )

    existing_record = await get_medical_record_by_chart_number(db, chart_number)

    if existing_record is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 진료 차트 넘버입니다.",
        )

    image_url = await save_xray_image_file(xray_image)

    medical_record, saved_xray_image = await create_medical_record_with_xray(
        db=db,
        patient_id=patient_id,
        chart_number=chart_number,
        symptoms=symptoms,
        image_url=image_url,
        shooting_datetime=shooting_datetime,
        uploader_id=current_user.id,
    )

    return {
        "id": medical_record.id,
        "patient_id": medical_record.patient_id,
        "chart_number": medical_record.chart_number,
        "symptoms": medical_record.symptoms,
        "xray_image": saved_xray_image,
        "created_at": medical_record.created_at,
        "updated_at": medical_record.updated_at,
    }


# 진료기록 목록용 증상 문자열을 만드는 함수
# 역할:
# - 증상이 100자를 초과하면 말줄임표를 붙여 목록에서 보기 좋게 만든다.
def summarize_symptoms(symptoms: str) -> str:
    if len(symptoms) <= 100:
        return symptoms

    return f"{symptoms[:100]}..."


# 진료기록 목록 조회 비즈니스 로직 함수
# 역할:
# - 환자 존재 여부를 확인한다.
# - page, size 값을 검증한다.
# - 해당 환자의 진료기록 목록과 전체 개수를 반환한다.
async def get_medical_records(
    db: AsyncSession,
    patient_id: int,
    page: int = 1,
    size: int = 20,
):
    patient = await get_patient_by_id(db, patient_id)

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="환자를 찾을 수 없습니다.",
        )

    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="page는 1 이상이어야 합니다.",
        )

    if size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="size는 1 이상이어야 합니다.",
        )

    medical_records = await get_medical_record_list_by_patient_id(
        db=db,
        patient_id=patient_id,
        page=page,
        size=size,
    )

    total = await count_medical_record_list_by_patient_id(
        db=db,
        patient_id=patient_id,
    )

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": [
            {
                "id": record.id,
                "chart_number": record.chart_number,
                "symptoms": summarize_symptoms(record.symptoms),
                "created_at": record.created_at,
            }
            for record in medical_records
        ],
    }


# 진료기록 상세 조회 비즈니스 로직 함수
# 역할:
# - 환자 존재 여부를 먼저 확인한다.
# - 요청한 환자에게 속한 진료기록인지 확인한다.
# - 진료기록과 연결된 X-Ray 이미지 목록을 반환한다.
async def get_medical_record_detail_info(
    db: AsyncSession,
    patient_id: int,
    record_id: int,
):
    patient = await get_patient_by_id(db, patient_id)

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="환자를 찾을 수 없습니다.",
        )

    medical_record = await get_medical_record_detail(
        db=db,
        patient_id=patient_id,
        record_id=record_id,
    )

    if medical_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="진료기록을 찾을 수 없습니다.",
        )

    return medical_record
