from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict
from app.schemas.appointment import AppointmentResponse


class PatientResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatientAppointmentsResponse(BaseModel):
    patient_id: str
    total_upcoming: int
    appointments: List[AppointmentResponse]
