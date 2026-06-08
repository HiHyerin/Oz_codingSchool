from fastapi import APIRouter, Depends, status, Response, Cookie, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.db.databases import async_get_db
from app.models.user import User
from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    LoginResponse,
    TokenRefreshResponse,
    LogoutResponse,
)
from app.services.auth_service import signup, login, refresh_access_token, logout

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


# access_token은 응답 body로 내려준다.
# refresh_token은 HttpOnly Cookie로 내려준다.
@router.post(
    "/login/",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login_handler(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(async_get_db),
):
    login_result = await login(db, request)

    # refresh_token은 JavaScript에서 접근하지 못하도록 HttpOnly Cookie로 저장한다.
    response.set_cookie(
        key="refresh_token",
        value=login_result["refresh_token"],
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax",
    )

    # response_model에는 refresh_token 필드가 없으므로 body에서는 제외한다.
    return {
        "access_token": login_result["access_token"],
        "token_type": login_result["token_type"],
        "user": login_result["user"],
    }


@router.post(
    "/refresh/",
    response_model=TokenRefreshResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh_token_handler(
    # 쿠키에서 refresh_token 값을 읽는다.
    # refresh_token 쿠키가 없으면 None이 들어온다.
    refresh_token: str | None = Cookie(default=None),
):
    # refresh_token이 아예 없으면 재발급 불가
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token이 없습니다. 다시 로그인해 주세요.",
        )
    return await refresh_access_token(refresh_token)


# 로그아웃 API endpoint
# 역할:
# - 클라이언트의 refresh_token 쿠키를 삭제한다.
# - access_token은 보통 클라이언트 메모리/localStorage/sessionStorage에서 직접 제거한다.
# - 현재 서버가 refresh_token을 DB에 저장하지 않으므로 서버 측 무효화 처리는 하지 않는다.
@router.post(
    "/logout/",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
)
async def logout_handler(
    # 쿠키 삭제를 위해 Response 객체를 받는다.
    response: Response,
    # Authorization: Bearer <access_token> 헤더를 검증한다.
    # 이 값이 없거나 잘못되면 여기서 401 에러가 발생한다.
    current_user: User = Depends(get_current_user),
):
    # refresh_token 쿠키 삭제
    # set_cookie로 만든 쿠키와 key/path가 같아야 정상 삭제된다.
    response.delete_cookie(
        key="refresh_token",
        path="/",
        samesite="lax",
    )

    # 로그아웃 결과 메시지 반환
    return await logout()
