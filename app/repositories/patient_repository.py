from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import Gender
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


# 환자 목록을 조회하는 함수
# 역할:
# - 이름 검색, 성별 필터, 나이 범위 필터를 적용해 환자 목록을 조회한다.
# - page, size 값으로 페이지네이션을 처리한다.
async def get_patient_list(
    db: AsyncSession,
    search: str | None = None,
    gender: Gender | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
    page: int = 1,
    size: int = 20,
) -> list[Patient]:
    query = select(Patient)

    # 이름 검색
    if search:
        query = query.where(Patient.name.like(f"%{search}%"))

    # 성별 필터
    if gender:
        query = query.where(Patient.gender == gender)

    # 최소 나이 필터
    if min_age is not None:
        query = query.where(Patient.age >= min_age)

    # 최대 나이 필터
    if max_age is not None:
        query = query.where(Patient.age <= max_age)

    # 최신 등록 환자 순으로 정렬
    query = query.order_by(Patient.id.desc())

    # 페이지네이션
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    result = await db.execute(query)

    return list(result.scalars().all())


# 환자 목록의 전체 개수를 조회하는 함수
# 역할:
# - 목록 조회와 같은 검색/필터 조건을 적용한 total 값을 계산한다.
async def count_patient_list(
    db: AsyncSession,
    search: str | None = None,
    gender: Gender | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
) -> int:
    query = select(func.count(Patient.id))

    if search:
        query = query.where(Patient.name.like(f"%{search}%"))

    if gender:
        query = query.where(Patient.gender == gender)

    if min_age is not None:
        query = query.where(Patient.age >= min_age)

    if max_age is not None:
        query = query.where(Patient.age <= max_age)

    result = await db.execute(query)

    return result.scalar_one()
