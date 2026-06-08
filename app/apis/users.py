from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.user import UserListResponse
from app.services.user_service import get_users

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
