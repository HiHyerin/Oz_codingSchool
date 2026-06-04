from app.schemas.ai_analysis_result import (
    AiAnalysisResultCreate,
    AiAnalysisResultRead,
    AiAnalysisResultUpdate,
)
from app.schemas.enums import Department, Gender, Role
from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordRead,
    MedicalRecordUpdate,
)
from app.schemas.patient import PatientCreate, PatientRead, PatientUpdate
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.xray_image import XrayImageCreate, XrayImageRead, XrayImageUpdate

__all__ = [
    "AiAnalysisResultCreate",
    "AiAnalysisResultRead",
    "AiAnalysisResultUpdate",
    "Department",
    "Gender",
    "MedicalRecordCreate",
    "MedicalRecordRead",
    "MedicalRecordUpdate",
    "PatientCreate",
    "PatientRead",
    "PatientUpdate",
    "Role",
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "XrayImageCreate",
    "XrayImageRead",
    "XrayImageUpdate",
]
