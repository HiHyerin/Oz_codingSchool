# DB 조회/저장 담당

from sqlalchemy import select
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
