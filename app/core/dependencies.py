from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.security import verify_access_token
from app.models.user import User
from app.models.enums import Role
from app.repositories.user_repository import get_user_by_id

# Authorization: Bearer <access_token> 형식의 헤더를 읽기 위한 객체
# 역할:
# - 요청 헤더에서 Bearer 토큰을 자동으로 추출한다.
bearer_scheme = HTTPBearer()


# 현재 로그인한 사용자를 가져오는 dependency
# 역할:
# - Authorization 헤더에서 access_token을 받는다.
# - access_token을 검증한다.
# - token 안의 user_id로 DB에서 사용자를 조회한다.
# - 인증이 필요한 API에서 Depends로 사용한다.
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(async_get_db),
) -> User:
    # Authorization 헤더에서 Bearer 뒤의 토큰 문자열만 꺼낸다.
    access_token = credentials.credentials

    # access_token 검증 후 user_id 추출
    user_id = verify_access_token(access_token)

    # user_id로 DB에서 사용자 조회
    user = await get_user_by_id(db, user_id)

    # 토큰은 정상이어도 DB에 사용자가 없으면 인증 실패
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다.",
        )

    return user


# 현재 사용자가 관리자 권한인지 확인하는 dependency
# 역할:
# - Authorization 헤더의 access_token을 검증해서 현재 사용자를 가져온다.
# - 현재 사용자의 role이 ADMIN인지 확인한다.
# - ADMIN이면 User 객체를 반환한다.
# - ADMIN이 아니면 403 Forbidden 에러를 발생시킨다.
async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다.",
        )

    return current_user
