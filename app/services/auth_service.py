from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
    create_access_token,
    verify_password,
    create_refresh_token,
    verify_refresh_token,
)
from app.models.enums import Role
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
    get_user_by_phone_number,
)
from app.schemas.auth import SignupRequest, LoginRequest

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


async def login(db: AsyncSession, request: LoginRequest):
    # 사용자 조회
    user = await get_user_by_email(db, request.email)

    # 사용자가 없으면 로그인 실패 처리
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이메일 또는 비밀번호가 일치하지 않습니다.",
        )

    # 비밀번호 비교
    is_valid_password = verify_password(
        request.password,
        user.hashed_password,
    )

    if not is_valid_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이메일 또는 비밀번호가 일치하지 않습니다.",
        )

    # 로그인 성공시 jwt access token 생성
    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)
    # 라우터에서 LoginResponse 형태로 변환되어 응답
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


async def refresh_access_token(refresh_token: str):
    user_id = verify_refresh_token(refresh_token)

    new_access_token = create_access_token(user_id=user_id)

    return {"access_token": new_access_token, "token_type": "bearer"}


# 로그아웃 비즈니스 로직 함수
# 역할:
# - 서버 측에서 별도 refresh token 저장소를 운영하지 않는 현재 구조에서는
#   로그아웃 성공 메시지만 생성한다.
# - 실제 refresh_token 쿠키 삭제는 Response 객체가 필요한 라우터에서 처리한다.
#
# 반환값:
# - 로그아웃 완료 메시지 dict
async def logout():
    return {
        "detail": "로그아웃되었습니다.",
    }
