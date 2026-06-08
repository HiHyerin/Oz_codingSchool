from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.enums import Role
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
    get_user_by_phone_number,
)
from app.schemas.auth import SignupRequest

# signup 함수에서 할 일

# 1. 이메일 중복이면 400 에러
# 2. 휴대폰 번호 중복이면 400 에러
# 3. password를 hashed_password로 변환
# 4. role은 PENDING으로 지정
# 5. repository.create_user 호출
# 6. 생성된 user 반환


async def signup(db: AsyncSession, request: SignupRequest):
    existing_email_user = await get_user_by_email(db, request.email)

    if existing_email_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 이메일입니다.",
        )

    existing_phone_user = await get_user_by_phone_number(
        db,
        request.phone_number,
    )

    if existing_phone_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 휴대폰 번호입니다.",
        )

    user_data = {
        "email": request.email,
        "hashed_password": hash_password(request.password),
        "name": request.name,
        "department": request.department,
        "gender": request.gender,
        "phone_number": request.phone_number,
        "role": Role.PENDING,
        "is_active": True,
    }

    user = await create_user(db, user_data)
    return user
