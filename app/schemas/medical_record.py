from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MedicalRecordBase(BaseModel):
    patient_id: int
    chart_number: str
    symptoms: str


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordUpdate(BaseModel):
    patient_id: int | None = None
    chart_number: str | None = None
    symptoms: str | None = None


class MedicalRecordRead(MedicalRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime | None = None
