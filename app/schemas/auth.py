from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.enums import Department, Gender, Role

# ConfigDict : SQLAlchemy 모델 객체를 Pydantic 응답 모델로 변환할 수 있게 설정할 때 사용


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    department: Department
    gender: Gender
    phone_number: str


class SignupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    name: str
    department: Department
    gender: Gender
    phone_number: str
    role: Role
    is_active: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    role: Role


class LoginResponse(BaseModel):
    access_token: str

    # 토큰 타입
    # 일반적으로 Bearer 인증 방식을 사용하므로 "bearer"를 반환한다.
    token_type: str

    user: LoginUserResponse
