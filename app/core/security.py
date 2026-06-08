from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.config import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 비밀번호 해싱 함수
def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    # 현재 UTC 시간
    now = datetime.now(timezone.utc)

    # 토큰 만료 시간
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # jwt payload
    payload = {
        "user_id": user_id,
        "exp": expire,
    }

    # payload를 SECRET_KEY와 ALGORITHM으로 암호화해서 JWT 문자열 생성
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
