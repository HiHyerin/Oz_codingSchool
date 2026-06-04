from datetime import datetime

from sqlalchemy import DateTime, Enum, SmallInteger, String, BigInteger, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.databases import Base
from app.models.enums import Gender


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    age: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender), nullable=True)
    phone: Mapped[str] = mapped_column(String(11), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("current_timestamp")
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, onupdate=datetime.now
    )

    medical_records = relationship(
        "MedicalRecord", back_populates="patient", cascade="all, delete-orphan"
    )
