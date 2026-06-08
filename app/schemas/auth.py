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
