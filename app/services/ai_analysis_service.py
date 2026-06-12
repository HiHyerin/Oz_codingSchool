from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.ai_analysis_result_repository import (
    count_ai_analysis_result_list_by_record_id,
    create_ai_analysis_result,
    get_ai_analysis_result_by_record_and_model,
    get_ai_analysis_result_list_by_record_id,
    get_ai_analysis_result_detail,
)
from app.repositories.medical_record_repository import get_medical_record_detail
from app.repositories.patient_repository import get_patient_by_id
from app.repositories.xray_image_repository import get_first_xray_image_by_record_id
from app.schemas.ai_analysis_result import AiPneumoniaPredictionRequest
from worker.model import predict_pneumonia

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# DB에 저장된 image_url을 실제 로컬 파일 경로로 변환하는 함수
# 역할:
# - "/media/xray/abc.jpeg" 같은 URL을 프로젝트 루트 기준 실제 파일 경로로 바꾼다.
def image_url_to_file_path(image_url: str) -> Path:
    return BASE_DIR / image_url.lstrip("/")


# AI 폐렴 예측 비즈니스 로직 함수
# 역할:
# - 환자와 진료기록 존재 여부를 확인한다.
# - 기존 예측 결과가 있으면 재추론하지 않고 반환한다.
# - 기존 결과가 없으면 X-Ray 이미지로 AI 모델 예측을 수행한다.
# - 예측 결과를 DB에 저장하고 응답한다.
async def predict_pneumonia_for_medical_record(
    db: AsyncSession,
    patient_id: int,
    record_id: int,
    request: AiPneumoniaPredictionRequest,
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

    existing_result = await get_ai_analysis_result_by_record_and_model(
        db=db,
        record_id=record_id,
        ai_model=request.ai_model,
    )

    if existing_result is not None:
        return {
            "id": existing_result.id,
            "record_id": existing_result.record_id,
            "is_pneumonia": existing_result.is_pneumonia,
            "prediction_label": (
                "PNEUMONIA" if existing_result.is_pneumonia else "NORMAL"
            ),
            "confidence": float(existing_result.confidence),
            "normal_probability": (
                1 - float(existing_result.confidence)
                if existing_result.is_pneumonia
                else float(existing_result.confidence)
            ),
            "pneumonia_probability": (
                float(existing_result.confidence)
                if existing_result.is_pneumonia
                else 1 - float(existing_result.confidence)
            ),
            "heatmap_url": existing_result.heatmap_url,
            "ai_model": existing_result.ai_model,
            "is_cached": True,
            "created_at": existing_result.created_at,
            "updated_at": existing_result.updated_at,
        }

    xray_image = await get_first_xray_image_by_record_id(
        db=db,
        record_id=record_id,
    )

    if xray_image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="예측에 사용할 X-Ray 이미지를 찾을 수 없습니다.",
        )

    image_path = image_url_to_file_path(xray_image.image_url)

    if not image_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="X-Ray 이미지 파일을 찾을 수 없습니다.",
        )

    prediction = predict_pneumonia(image_path)

    is_pneumonia = prediction["label"] == "PNEUMONIA"

    saved_result = await create_ai_analysis_result(
        db=db,
        record_id=record_id,
        is_pneumonia=is_pneumonia,
        confidence=prediction["confidence"],
        heatmap_url="",
        ai_model=request.ai_model,
    )

    return {
        "id": saved_result.id,
        "record_id": saved_result.record_id,
        "is_pneumonia": saved_result.is_pneumonia,
        "prediction_label": prediction["label"],
        "confidence": prediction["confidence"],
        "normal_probability": prediction["normal_probability"],
        "pneumonia_probability": prediction["pneumonia_probability"],
        "heatmap_url": saved_result.heatmap_url,
        "ai_model": saved_result.ai_model,
        "is_cached": False,
        "created_at": saved_result.created_at,
        "updated_at": saved_result.updated_at,
    }


# AI 폐렴 예측 결과 목록 조회 비즈니스 로직 함수
# 역할:
# - 환자와 진료기록 존재 여부를 확인한다.
# - page, size 값을 검증한다.
# - 해당 진료기록의 AI 예측 결과 목록과 전체 개수를 반환한다.
async def get_ai_analysis_results(
    db: AsyncSession,
    patient_id: int,
    record_id: int,
    page: int = 1,
    size: int = 20,
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

    ai_analysis_results = await get_ai_analysis_result_list_by_record_id(
        db=db,
        record_id=record_id,
        page=page,
        size=size,
    )

    total = await count_ai_analysis_result_list_by_record_id(
        db=db,
        record_id=record_id,
    )

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": ai_analysis_results,
    }


# AI 폐렴 예측 결과 상세 조회 비즈니스 로직 함수
# 역할:
# - 환자 존재 여부를 확인한다.
# - 진료기록 존재 여부를 확인한다.
# - AI 예측 결과가 해당 진료기록에 속하는지 확인한다.
# - 상세 응답 dict를 반환한다.
async def get_ai_analysis_result_detail_info(
    db: AsyncSession,
    patient_id: int,
    record_id: int,
    analysis_id: int,
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

    ai_analysis_result = await get_ai_analysis_result_detail(
        db=db,
        record_id=record_id,
        analysis_id=analysis_id,
    )

    if ai_analysis_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI 예측 결과를 찾을 수 없습니다.",
        )

    return {
        "id": ai_analysis_result.id,
        "record_id": ai_analysis_result.record_id,
        "is_pneumonia": ai_analysis_result.is_pneumonia,
        "prediction_label": (
            "PNEUMONIA" if ai_analysis_result.is_pneumonia else "NORMAL"
        ),
        "confidence": float(ai_analysis_result.confidence),
        "heatmap_url": ai_analysis_result.heatmap_url,
        "ai_model": ai_analysis_result.ai_model,
        "created_at": ai_analysis_result.created_at,
        "updated_at": ai_analysis_result.updated_at,
    }
