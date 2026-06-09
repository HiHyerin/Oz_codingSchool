from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_staff_user
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientRead
from app.services.patient_service import register_patient

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
