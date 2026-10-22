import uuid
from datetime import time
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Time, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.doctor import Doctor


class DoctorWorkingHours(Base, TimestampMixin):
    """Defines recurring weekly working schedule for a doctor."""
    __tablename__ = "doctor_working_hours"

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
    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday"
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="working_hours")

    __table_args__ = (
        UniqueConstraint("doctor_id", "day_of_week", name="uq_doctor_day_of_week"),
    )

    def __repr__(self) -> str:
        return f"<DoctorWorkingHours doctor={self.doctor_id} day={self.day_of_week} {self.start_time}-{self.end_time}>"
