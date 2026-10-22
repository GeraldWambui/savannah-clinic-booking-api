import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.schedule import DoctorWorkingHours
    from app.models.appointment import Appointment


class Doctor(Base, TimestampMixin):
    __tablename__ = "doctors"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    specialization: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    working_hours: Mapped[List["DoctorWorkingHours"]] = relationship(
        "DoctorWorkingHours",
        back_populates="doctor",
        cascade="all, delete-orphan",
        order_by="DoctorWorkingHours.day_of_week"
    )
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment",
        back_populates="doctor",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Doctor {self.name} ({self.specialization})>"
