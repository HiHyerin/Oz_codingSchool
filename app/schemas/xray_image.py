from datetime import datetime

from pydantic import BaseModel, ConfigDict


class XrayImageBase(BaseModel):
    record_id: int
    uploader_id: int | None = None
    image_url: str
    shooting_datetime: datetime


class XrayImageCreate(XrayImageBase):
    pass


class XrayImageUpdate(BaseModel):
    record_id: int | None = None
    uploader_id: int | None = None
    image_url: str | None = None
    shooting_datetime: datetime | None = None


class XrayImageRead(XrayImageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
