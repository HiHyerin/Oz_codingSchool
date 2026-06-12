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


# 진료기록 등록 응답의 X-Ray 이미지 정보 클래스
# 역할:
# - 진료기록 등록 후 함께 저장된 X-Ray 이미지 정보를 응답한다.
class MedicalRecordXrayImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # X-Ray 이미지 고유 ID
    id: int

    # 서버에 저장된 이미지 접근 URL
    image_url: str

    # X-Ray 촬영 일시
    shooting_datetime: datetime


# 진료기록 등록 응답 클래스
# 역할:
# - 진료기록과 업로드된 X-Ray 이미지 정보를 함께 응답한다.
class MedicalRecordCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # 진료기록 고유 ID
    id: int

    # 환자 고유 ID
    patient_id: int

    # 진료 차트 넘버
    chart_number: str

    # 진료된 증상
    symptoms: str

    # 함께 업로드된 X-Ray 이미지 정보
    xray_image: MedicalRecordXrayImageResponse

    # 생성일시
    created_at: datetime

    # 수정일시
    updated_at: datetime | None = None


# 진료기록 목록의 개별 항목 응답 클래스
# 역할:
# - 환자 상세 화면의 진료기록 목록에서 보여줄 필드만 정의한다.
class MedicalRecordListItemResponse(BaseModel):
    # 진료기록 고유 ID
    id: int

    # 진료 차트 넘버
    chart_number: str

    # 증상 요약
    symptoms: str

    # 생성일시
    created_at: datetime


# 진료기록 목록 조회 응답 클래스
# 역할:
# - 특정 환자의 진료기록 목록과 페이지네이션 정보를 응답한다.
class MedicalRecordListResponse(BaseModel):
    # 해당 환자의 전체 진료기록 수
    total: int

    # 현재 페이지 번호
    page: int

    # 페이지당 조회 수
    size: int

    # 진료기록 목록
    items: list[MedicalRecordListItemResponse]


# 진료기록 상세 응답의 X-Ray 이미지 정보 클래스
# 역할:
# - 진료기록 상세 화면에서 표시할 X-Ray 이미지 정보를 정의한다.
class MedicalRecordDetailXrayImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # X-Ray 이미지 고유 ID
    id: int

    # 서버에 저장된 이미지 접근 URL
    image_url: str

    # X-Ray 촬영 일시
    shooting_datetime: datetime

    # 이미지 생성일시
    created_at: datetime


# 진료기록 상세 조회 응답 클래스
# 역할:
# - 진료기록 상세 정보와 연결된 X-Ray 이미지 목록을 응답한다.
class MedicalRecordDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # 진료기록 고유 ID
    id: int

    # 환자 고유 ID
    patient_id: int

    # 진료 차트 넘버
    chart_number: str

    # 진료된 증상
    symptoms: str

    # 연결된 X-Ray 이미지 목록
    xray_images: list[MedicalRecordDetailXrayImageResponse]

    # 생성일시
    created_at: datetime

    # 수정일시
    updated_at: datetime | None = None
