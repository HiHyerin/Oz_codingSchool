from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import Gender
from app.repositories.patient_repository import (
    count_patient_list,
    create_patient,
    get_patient_list,
)
from app.schemas.patient import PatientCreate


# 환자 정보 등록 비즈니스 로직 함수
# 역할:
# - 환자 등록 요청 데이터를 검증한다.
# - repository를 호출해 환자 정보를 DB에 저장한다.
# - 생성된 환자 정보를 반환한다.
async def register_patient(
    db: AsyncSession,
    request: PatientCreate,
):
    # 나이는 0보다 커야 한다.
    if request.age <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="나이는 1 이상이어야 합니다.",
        )

    # 연락처는 DB 모델 기준 String(11)이므로 숫자 11자리 형식을 권장한다.
    if not request.phone.isdigit() or len(request.phone) != 11:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="연락처는 숫자 11자리여야 합니다.",
        )

    patient_data = {
        "name": request.name,
        "age": request.age,
        "gender": request.gender,
        "phone": request.phone,
    }

    patient = await create_patient(
        db=db,
        patient_data=patient_data,
    )

    return patient


# 환자 목록 조회 비즈니스 로직 함수
# 역할:
# - 검색/필터/페이지네이션 요청값을 검증한다.
# - repository를 호출해 환자 목록과 전체 개수를 조회한다.
# - API 응답 형식에 맞게 total, page, size, items를 묶어 반환한다.
async def get_patients(
    db: AsyncSession,
    search: str | None = None,
    gender: Gender | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
    page: int = 1,
    size: int = 20,
):
    # Query에서 ge=1 검증을 하더라도 service에서도 한 번 더 방어한다.
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

    if min_age is not None and min_age < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_age는 0 이상이어야 합니다.",
        )

    if max_age is not None and max_age < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="max_age는 0 이상이어야 합니다.",
        )

    if min_age is not None and max_age is not None and min_age > max_age:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="나이 범위가 올바르지 않습니다.",
        )

    patients = await get_patient_list(
        db=db,
        search=search,
        gender=gender,
        min_age=min_age,
        max_age=max_age,
        page=page,
        size=size,
    )

    total = await count_patient_list(
        db=db,
        search=search,
        gender=gender,
        min_age=min_age,
        max_age=max_age,
    )

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": patients,
    }
