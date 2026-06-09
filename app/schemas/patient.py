from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.enums import Gender


# 환자 공통 필드 클래스
class PatientBase(BaseModel):
    name: str
    age: int
    gender: Gender | None = None
    phone: str


# 환자 정보 등록 요청 클래스
class PatientCreate(PatientBase):
    pass


# 환자 정보 수정 요청 클래스
class PatientUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    gender: Gender | None = None
    phone: str | None = None


# 환자 정보 응답 클래스
class PatientRead(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime | None = None
