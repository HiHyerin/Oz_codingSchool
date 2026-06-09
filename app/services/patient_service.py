from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.patient_repository import create_patient
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
