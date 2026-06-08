from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.enums import Department, Gender, Role


class UserBase(BaseModel):
    email: str
    name: str
    phone_number: str
    gender: Gender
    department: Department
    role: Role = Role.PENDING
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None
    name: str | None = None
    phone_number: str | None = None
    gender: Gender | None = None
    department: Department | None = None
    role: Role | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime | None = None


# 회원 목록의 개별 회원 응답 클래스
class UserListItemResponse(BaseModel):
    # SQLAlchemy User 객체를 Pydantic 응답 모델로 변환할 수 있게 한다.
    model_config = ConfigDict(from_attributes=True)

    # 사용자 고유 ID
    id: int

    # 사용자 이메일
    email: EmailStr

    # 사용자 이름
    name: str

    # 사용자 부서
    department: Department

    # 사용자 성별
    gender: Gender

    # 사용자 휴대폰 번호
    phone_number: str

    # 사용자 권한
    role: Role

    # 계정 활성화 여부
    is_active: bool


# 회원 목록 조회 응답 클래스
class UserListResponse(BaseModel):
    # 검색/필터 조건을 반영한 전체 회원 수
    total: int

    # 현재 페이지 번호
    page: int

    # 페이지당 조회 수
    size: int

    # 회원 목록
    items: list[UserListItemResponse]


# 회원 권한 변경 요청 클래스
class UserRoleUpdateRequest(BaseModel):
    # 변경할 권한
    # 허용 값: PENDING, STAFF, ADMIN
    role: Role


# 회원 권한 변경 응답 클래스
class UserRoleUpdateResponse(BaseModel):
    # SQLAlchemy User 객체를 Pydantic 응답 모델로 변환할 수 있게 한다.
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    role: Role

    # 수정 일시
    # updated_at이 아직 없을 수 있으므로 None 허용
    updated_at: datetime | None = None
