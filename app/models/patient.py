import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.appointment import Appointment


class Patient(Base, TimestampMixin):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)

    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment",
        back_populates="patient",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Patient {self.name}>"
