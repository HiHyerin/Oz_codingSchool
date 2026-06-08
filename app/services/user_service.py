from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import Department
from app.repositories.user_repository import count_user_list, get_user_list


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
