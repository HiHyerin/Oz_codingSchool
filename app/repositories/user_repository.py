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
