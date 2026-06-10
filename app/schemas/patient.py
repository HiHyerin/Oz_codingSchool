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
    # 변경할 환자 이름
    name: str | None = None

    # 변경할 환자 연락처
    phone: str | None = None


# 환자 정보 응답 클래스
class PatientRead(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime | None = None


# 환자 목록 조회 응답 클래스
# 역할:
# - 환자 목록 조회 API의 응답 구조를 정의한다.
# - total, page, size와 실제 환자 목록 items를 함께 반환한다.
class PatientListResponse(BaseModel):
    # 검색/필터 조건을 반영한 전체 환자 수
    total: int

    # 현재 페이지 번호
    page: int

    # 페이지당 조회 수
    size: int

    # 환자 목록
    items: list[PatientRead]
