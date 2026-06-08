from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.schemas.auth import SignupRequest, SignupResponse, LoginRequest, LoginResponse
from app.services.auth_service import signup, login

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/signup/",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup_handler(
    request: SignupRequest,
    db: AsyncSession = Depends(async_get_db),
):
    return await signup(db, request)


@router.post(
    "/login/",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login_handler(
    request: LoginRequest,
    db: AsyncSession = Depends(async_get_db),
):
    return await login(db, request)
