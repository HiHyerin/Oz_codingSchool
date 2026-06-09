from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient


# 환자 정보를 DB에 생성하는 함수
# 역할:
# - Patient 모델 객체를 생성한다.
# - DB에 저장한 뒤 생성된 id, created_at 등을 반영해서 반환한다.
async def create_patient(
    db: AsyncSession,
    patient_data: dict,
) -> Patient:
    # 요청 데이터를 SQLAlchemy Patient 모델 객체로 변환
    patient = Patient(**patient_data)

    # DB 세션에 추가
    db.add(patient)

    # INSERT 실행
    await db.commit()

    # DB에서 생성된 id, created_at 등을 객체에 반영
    await db.refresh(patient)

    return patient
