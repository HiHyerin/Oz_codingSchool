from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_admin_user, get_current_user
from app.models.user import User
from app.schemas.user import (
    UserListResponse,
    UserRoleUpdateRequest,
    UserRoleUpdateResponse,
)
from app.services.user_service import get_users, change_user_role, get_my_page
from app.schemas.user import MyPageResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# 회원 목록 조회 API endpoint
# 역할:
# - 관리자 권한 사용자가 전체 회원 목록을 조회한다.
# - search query로 이메일 또는 이름 검색을 지원한다.
# - department query로 부서 필터를 지원한다.
# - page, size query로 페이지네이션을 지원한다.
@router.get(
    "/",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_users_handler(
    # 이메일 또는 이름 검색어
    search: str | None = Query(default=None),
    # 부서 필터
    # 허용 값: RESEARCH, MEDICAL, DEV
    department: str | None = Query(default=None),
    # 페이지 번호
    page: int = Query(default=1, ge=1),
    # 페이지당 조회 수
    size: int = Query(default=20, ge=1),
    # DB 세션
    db: AsyncSession = Depends(async_get_db),
    # 관리자 인증/인가
    # Authorization 헤더의 access_token을 검증하고 ADMIN 권한인지 확인한다.
    current_admin: User = Depends(get_current_admin_user),
):
    return await get_users(
        db=db,
        search=search,
        department=department,
        page=page,
        size=size,
    )


# 마이페이지 조회 API endpoint
# 역할:
# - Authorization 헤더의 access_token을 검증한다.
# - 로그인한 사용자의 본인 정보를 반환한다.
# - PENDING, STAFF, ADMIN 모두 접근 가능하다.
@router.get(
    "/me/",
    response_model=MyPageResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_page_handler(
    # 현재 로그인 사용자
    # access_token이 없거나 잘못되면 401 에러가 발생한다.
    current_user: User = Depends(get_current_user),
):
    return await get_my_page(current_user)


# 회원 권한 변경 API endpoint
# 역할:
# - 관리자 권한 사용자가 특정 회원의 권한을 변경한다.
# - path parameter로 변경 대상 user_id를 받는다.
# - request body로 변경할 role을 받는다.
@router.patch(
    "/{user_id}/role/",
    response_model=UserRoleUpdateResponse,
    status_code=status.HTTP_200_OK,
)
async def change_user_role_handler(
    # 권한을 변경할 대상 회원 ID
    user_id: int,
    # 변경할 권한 정보
    request: UserRoleUpdateRequest,
    # DB 세션
    db: AsyncSession = Depends(async_get_db),
    # 관리자 인증/인가
    # ADMIN 권한이 아니면 403 에러 발생
    current_admin: User = Depends(get_current_admin_user),
):
    return await change_user_role(
        db=db,
        user_id=user_id,
        request=request,
    )
