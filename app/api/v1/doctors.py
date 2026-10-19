from datetime import date
from typing import List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorResponse
from app.schemas.availability import DoctorAvailabilityResponse, SlotResponse
from app.services.availability import get_available_slots_for_doctor
from app.core.exceptions import DoctorNotFoundException

router = APIRouter()


@router.get(
    "",
    response_model=List[DoctorResponse],
    summary="List all active doctors",
    description="Returns all active doctors and their recurring weekly working schedules."
)
def list_doctors(db: Session = Depends(get_db)):
    stmt = select(Doctor).where(Doctor.is_active.is_(True))
    doctors = db.scalars(stmt).all()
    return doctors


@router.get(
    "/{id}",
    response_model=DoctorResponse,
    summary="Get doctor by ID"
)
def get_doctor(id: str, db: Session = Depends(get_db)):
    doctor = db.get(Doctor, id)
    if not doctor or not doctor.is_active:
        raise DoctorNotFoundException(id)
    return doctor


@router.get(
    "/{id}/availability",
    response_model=DoctorAvailabilityResponse,
    summary="Get doctor availability slots",
    description="Return all available 30-minute slots for a doctor on a given date (YYYY-MM-DD)."
)
def get_doctor_availability(
    id: str,
    date: date = Query(..., description="Target date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    slots = get_available_slots_for_doctor(db, doctor_id=id, target_date=date)
    return DoctorAvailabilityResponse(
        doctor_id=id,
        date=date,
        total_slots=len(slots),
        available_slots=[SlotResponse(**s) for s in slots]
    )
