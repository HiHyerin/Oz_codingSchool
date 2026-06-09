from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_staff_user
from app.models.enums import Gender
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientListResponse, PatientRead
from app.services.patient_service import get_patients, register_patient

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


# 환자 정보 등록 API endpoint
@router.post(
    "/",
    response_model=PatientRead,
    status_code=status.HTTP_201_CREATED,
)
async def register_patient_handler(
    # 환자 등록 요청 body
    request: PatientCreate,
    # DB 세션
    db: AsyncSession = Depends(async_get_db),
    # STAFF 또는 ADMIN 권한 인증/인가
    current_user: User = Depends(get_current_staff_user),
):
    return await register_patient(
        db=db,
        request=request,
    )


# 환자 목록 조회 API endpoint
# 역할:
# - STAFF 또는 ADMIN 권한 사용자가 환자 목록을 조회한다.
# - 이름 검색, 성별 필터, 나이 범위 필터, 페이지네이션을 지원한다.
@router.get(
    "/",
    response_model=PatientListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_patients_handler(
    # 환자 이름 검색어
    search: str | None = Query(default=None),
    # 성별 필터
    gender: Gender | None = Query(default=None),
    # 최소 나이
    min_age: int | None = Query(default=None, ge=0),
    # 최대 나이
    max_age: int | None = Query(default=None, ge=0),
    # 페이지 번호
    page: int = Query(default=1, ge=1),
    # 페이지당 조회 수
    size: int = Query(default=20, ge=1),
    # DB 세션
    db: AsyncSession = Depends(async_get_db),
    # STAFF 또는 ADMIN 권한 인증/인가
    current_user: User = Depends(get_current_staff_user),
):
    return await get_patients(
        db=db,
        search=search,
        gender=gender,
        min_age=min_age,
        max_age=max_age,
        page=page,
        size=size,
    )
