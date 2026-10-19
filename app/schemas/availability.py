from datetime import date
from typing import List
from pydantic import BaseModel


class SlotResponse(BaseModel):
    doctor_id: str
    start_time: str
    end_time: str
    duration_minutes: int


class DoctorAvailabilityResponse(BaseModel):
    doctor_id: str
    date: date
    total_slots: int
    available_slots: List[SlotResponse]
