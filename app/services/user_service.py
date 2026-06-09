from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import Department
from app.models.enums import Role
from app.models.user import User
from app.repositories.user_repository import (
    count_user_list,
    get_user_list,
    get_user_by_id,
    update_user_role,
)
from app.schemas.user import UserRoleUpdateRequest


# 회원 목록 조회 비즈니스 로직 함수
# 역할:
# - page, size 값이 올바른지 검증한다.
# - department 값이 enum에 존재하는지 검증한다.
# - repository를 호출해 회원 목록과 전체 개수를 조회한다.
# - API 응답 형태에 맞게 dict로 묶어 반환한다.
#
# 매개변수:
# - db: 비동기 DB 세션
# - search: 이메일 또는 이름 검색어
# - department: 부서 필터
# - page: 현재 페이지 번호
# - size: 페이지당 조회 수
#
# 반환값:
# - total, page, size, items를 담은 dict
async def get_users(
    db: AsyncSession,
    search: str | None = None,
    department: str | None = None,
    page: int = 1,
    size: int = 20,
):
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

    if department and department not in Department.__members__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바르지 않은 부서 값입니다.",
        )

    users = await get_user_list(
        db=db,
        search=search,
        department=department,
        page=page,
        size=size,
    )

    total = await count_user_list(
        db=db,
        search=search,
        department=department,
    )

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": users,
    }


# 회원 권한 변경 비즈니스 로직 함수
# 역할:
# - 변경 대상 회원이 존재하는지 확인한다.
# - 존재하지 않으면 404 에러를 발생시킨다.
# - 존재하면 repository를 통해 role을 변경한다.
async def change_user_role(
    db: AsyncSession,
    user_id: int,
    request: UserRoleUpdateRequest,
):
    # 권한 변경 대상 회원 조회
    user = await get_user_by_id(db, user_id)

    # 대상 회원이 없으면 404
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다.",
        )

    # 요청받은 role로 회원 권한 변경
    updated_user = await update_user_role(
        db=db,
        user=user,
        role=request.role,
    )

    return updated_user


# 마이페이지 조회 비즈니스 로직 함수
# 역할:
# - 현재 로그인한 사용자의 정보를 반환한다.
# - 현재 사용자 조회와 인증 검증은 get_current_user dependency에서 이미 처리된다.
#
# 매개변수:
# - current_user: access_token 검증 후 DB에서 조회된 현재 로그인 사용자
#
# 반환값:
# - 현재 로그인한 User 객체
# 비고:
# - 현재는 사실 의미없는 함수지만 나중에 확장가능성을 생각하여 만들어 놓았다.
async def get_my_page(current_user: User) -> User:
    return current_user
