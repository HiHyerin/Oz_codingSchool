from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.enums import Gender


class PatientBase(BaseModel):
    name: str
    age: int
    gender: Gender | None = None
    phone: str


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    gender: Gender | None = None
    phone: str | None = None


class PatientRead(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime | None = None
