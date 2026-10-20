from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AppointmentCreate(BaseModel):
    doctor_id: str = Field(..., description="UUID of the doctor")
    patient_id: str = Field(..., description="UUID of the patient")
    start_time: datetime = Field(..., description="Desired start time in UTC ISO-8601 format")


class AppointmentCancel(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500, description="Reason for cancellation")


class AppointmentReschedule(BaseModel):
    new_start_time: datetime = Field(..., description="New desired start time in UTC ISO-8601 format")


class AppointmentResponse(BaseModel):
    id: str
    doctor_id: str
    patient_id: str
    start_time: datetime
    end_time: datetime
    status: str
    cancellation_reason: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
