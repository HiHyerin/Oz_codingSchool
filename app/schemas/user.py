from datetime import datetime

from pydantic import BaseModel, ConfigDict

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
