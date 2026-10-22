import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, Text, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.models.enums import AppointmentStatus

if TYPE_CHECKING:
    from app.models.doctor import Doctor
    from app.models.patient import Patient


class Appointment(Base, TimestampMixin):
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    doctor_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    patient_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=AppointmentStatus.SCHEDULED.value,
        nullable=False,
        index=True
    )
    cancellation_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="appointments")
    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")

    __table_args__ = (
        Index(
            "uq_doctor_active_slot",
            "doctor_id",
            "start_time",
            unique=True,
            postgresql_where=(text("status != 'CANCELLED'")),
            sqlite_where=(text("status != 'CANCELLED'"))
        ),
    )

    def __repr__(self) -> str:
        return f"<Appointment {self.id} doctor={self.doctor_id} start={self.start_time} status={self.status}>"
