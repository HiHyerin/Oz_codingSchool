# DB 조회/저장 담당

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


# 이메일 중복 확인
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))

    return result.scalar_one_or_none()


# 휴대폰 번호 중복 확인
async def get_user_by_phone_number(
    db: AsyncSession,
    phone_number: str,
) -> User | None:
    result = await db.execute(select(User).where(User.phone_number == phone_number))

    return result.scalar_one_or_none()


# User 모델 생성 후 db.add, db.comit, db.refresh
async def create_user(db: AsyncSession, user_data: dict) -> User:
    user = User(**user_data)

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


# user_id로 사용자를 조회하는 함수
# 역할:
# - access_token에서 꺼낸 user_id가 실제 DB에 존재하는 사용자인지 확인한다.
# - 인증이 필요한 API에서 현재 로그인 사용자를 가져올 때 사용한다.
async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))

    return result.scalar_one_or_none()


# 회원 목록을 조회하는 함수
# 매개변수:
# - db: 비동기 DB 세션
# - search: 이메일 또는 이름 검색어
# - department: 부서 필터
# - page: 현재 페이지 번호
# - size: 페이지당 조회 수
#
# 반환값:
# - 조건에 맞는 User 객체 리스트
async def get_user_list(
    db: AsyncSession,
    search: str | None = None,
    department: str | None = None,
    page: int = 1,
    size: int = 20,
) -> list[User]:
    query = select(User)

    # 이메일 또는 이름 검색
    if search:
        search_keyword = f"%{search}%"
        query = query.where(
            or_(
                User.email.like(search_keyword),
                User.name.like(search_keyword),
            )
        )

    # 부서 필터
    if department:
        query = query.where(User.department == department)

    # 최신 가입자 순 정렬
    query = query.order_by(User.id.desc())

    # 페이지네이션
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    result = await db.execute(query)

    return list(result.scalars().all())


# 회원 목록 전체 개수를 조회하는 함수
# 역할:
# - 페이지네이션 응답의 total 값을 만들기 위해 사용한다.
# - search, department 조건은 목록 조회와 동일하게 반영한다.
async def count_user_list(
    db: AsyncSession,
    search: str | None = None,
    department: str | None = None,
) -> int:
    query = select(func.count(User.id))

    if search:
        search_keyword = f"%{search}%"
        query = query.where(
            or_(
                User.email.like(search_keyword),
                User.name.like(search_keyword),
            )
        )

    if department:
        query = query.where(User.department == department)

    result = await db.execute(query)

    return result.scalar_one()
