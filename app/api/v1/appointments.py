from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentCancel,
    AppointmentReschedule,
    AppointmentResponse,
)
from app.services.booking import (
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
)
from app.models.appointment import Appointment
from app.core.exceptions import AppointmentNotFoundException

router = APIRouter()


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Book an appointment",
    description="Book a 30-minute appointment slot. Validates doctor working hours, lead time, and double-booking."
)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db)
):
    appointment = book_appointment(
        db=db,
        doctor_id=payload.doctor_id,
        patient_id=payload.patient_id,
        start_time=payload.start_time
    )
    return appointment


@router.get(
    "/{id}",
    response_model=AppointmentResponse,
    summary="Get appointment details"
)
def get_appointment(id: str, db: Session = Depends(get_db)):
    appointment = db.get(Appointment, id)
    if not appointment:
        raise AppointmentNotFoundException(id)
    return appointment


@router.patch(
    "/{id}/cancel",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel an appointment",
    description="Cancel an appointment with a reason. Slot becomes available again for other patients."
)
def cancel_existing_appointment(
    id: str,
    payload: AppointmentCancel,
    db: Session = Depends(get_db)
):
    appointment = cancel_appointment(
        db=db,
        appointment_id=id,
        reason=payload.reason
    )
    return appointment


@router.patch(
    "/{id}/reschedule",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Reschedule an appointment",
    description="Move an appointment to a new slot. Original slot is freed and new slot is validated."
)
def reschedule_existing_appointment(
    id: str,
    payload: AppointmentReschedule,
    db: Session = Depends(get_db)
):
    appointment = reschedule_appointment(
        db=db,
        appointment_id=id,
        new_start_time=payload.new_start_time
    )
    return appointment
