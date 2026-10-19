from datetime import time
from typing import List
from pydantic import BaseModel, ConfigDict


class WorkingHoursResponse(BaseModel):
    id: str
    day_of_week: int
    start_time: time
    end_time: time
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class DoctorResponse(BaseModel):
    id: str
    name: str
    email: str
    specialization: str
    is_active: bool
    working_hours: List[WorkingHoursResponse] = []

    model_config = ConfigDict(from_attributes=True)
