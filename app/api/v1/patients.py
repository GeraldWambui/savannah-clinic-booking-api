from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.api.deps import get_db
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.schemas.patient import PatientResponse, PatientAppointmentsResponse
from app.schemas.appointment import AppointmentResponse
from app.core.exceptions import PatientNotFoundException

router = APIRouter()


@router.get(
    "",
    response_model=List[PatientResponse],
    summary="List all patients"
)
def list_patients(db: Session = Depends(get_db)):
    patients = db.scalars(select(Patient)).all()
    return patients


@router.get(
    "/{id}",
    response_model=PatientResponse,
    summary="Get patient details"
)
def get_patient(id: str, db: Session = Depends(get_db)):
    patient = db.get(Patient, id)
    if not patient:
        raise PatientNotFoundException(id)
    return patient


@router.get(
    "/{id}/appointments",
    response_model=PatientAppointmentsResponse,
    summary="Get upcoming appointments for a patient (Bonus)",
    description="Returns upcoming active appointments for a patient sorted chronologically by start date."
)
def get_patient_upcoming_appointments(
    id: str,
    db: Session = Depends(get_db)
):
    patient = db.get(Patient, id)
    if not patient:
        raise PatientNotFoundException(id)

    now_utc = datetime.now(timezone.utc)

    stmt = (
        select(Appointment)
        .where(
            and_(
                Appointment.patient_id == id,
                Appointment.status == AppointmentStatus.SCHEDULED.value,
                Appointment.start_time >= now_utc
            )
        )
        .order_by(Appointment.start_time.asc())
    )
    appointments = db.scalars(stmt).all()

    return PatientAppointmentsResponse(
        patient_id=id,
        total_upcoming=len(appointments),
        appointments=[AppointmentResponse.model_validate(a) for a in appointments]
    )
