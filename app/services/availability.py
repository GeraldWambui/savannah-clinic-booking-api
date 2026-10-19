from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.core.config import settings
from app.core.exceptions import DoctorNotFoundException
from app.models.doctor import Doctor
from app.models.schedule import DoctorWorkingHours
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus


def get_clinic_timezone() -> ZoneInfo:
    return ZoneInfo(settings.CLINIC_TIMEZONE)


def generate_candidate_slots(
    target_date: date,
    working_hours: DoctorWorkingHours
) -> List[tuple[datetime, datetime]]:
    """Generates all 30-minute slot tuples (start_utc, end_utc) for a given date and working hours."""
    clinic_tz = get_clinic_timezone()
    
    current_local = datetime.combine(target_date, working_hours.start_time, tzinfo=clinic_tz)
    end_local = datetime.combine(target_date, working_hours.end_time, tzinfo=clinic_tz)
    
    slot_delta = timedelta(minutes=settings.SLOT_DURATION_MINUTES)
    slots: List[tuple[datetime, datetime]] = []

    while current_local + slot_delta <= end_local:
        slot_start_utc = current_local.astimezone(timezone.utc)
        slot_end_utc = (current_local + slot_delta).astimezone(timezone.utc)
        slots.append((slot_start_utc, slot_end_utc))
        current_local += slot_delta

    return slots


def get_available_slots_for_doctor(
    db: Session,
    doctor_id: str,
    target_date: date,
    now_utc: datetime = None
) -> List[Dict[str, Any]]:
    """Calculates real-time available 30-minute slots for a doctor on a specific date.
    
    Enforces:
    - Doctor existence and active status
    - Working hours for target day of week
    - Exclusion of already booked (active) appointments
    - Exclusion of past slots
    - Exclusion of slots within 1 hour of now (Bonus requirement)
    """
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    # 1. Verify doctor exists and is active
    doctor = db.get(Doctor, doctor_id)
    if not doctor or not doctor.is_active:
        raise DoctorNotFoundException(doctor_id)

    # 2. Get doctor's working hours for the target day of week
    day_of_week = target_date.weekday()
    stmt_wh = select(DoctorWorkingHours).where(
        DoctorWorkingHours.doctor_id == doctor_id,
        DoctorWorkingHours.day_of_week == day_of_week,
        DoctorWorkingHours.is_active.is_(True)
    )
    working_hours = db.scalars(stmt_wh).first()
    if not working_hours:
        # Doctor doesn't work on this day
        return []

    # 3. Generate candidate slots
    candidate_slots = generate_candidate_slots(target_date, working_hours)
    if not candidate_slots:
        return []

    # 4. Filter out slots within the 1-hour booking cutoff
    cutoff_time = now_utc + timedelta(hours=settings.MIN_BOOKING_LEAD_HOURS)
    valid_candidate_slots = [
        (s_start, s_end) for s_start, s_end in candidate_slots
        if s_start >= cutoff_time
    ]

    if not valid_candidate_slots:
        return []

    # 5. Query active appointments for this doctor on the target date window
    day_start_utc = datetime.combine(target_date, datetime.min.time(), tzinfo=get_clinic_timezone()).astimezone(timezone.utc)
    day_end_utc = datetime.combine(target_date, datetime.max.time(), tzinfo=get_clinic_timezone()).astimezone(timezone.utc)

    stmt_appts = select(Appointment.start_time).where(
        and_(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.SCHEDULED.value,
            Appointment.start_time >= day_start_utc,
            Appointment.start_time <= day_end_utc
        )
    )
    booked_start_times = set(db.scalars(stmt_appts).all())

    # 6. Candidate slots minus booked slots = Available slots
    available_slots: List[Dict[str, Any]] = []
    for s_start, s_end in valid_candidate_slots:
        # Normalize comparison: SQLite or Postgres might return naive or aware
        is_booked = False
        for b_time in booked_start_times:
            if b_time.tzinfo is None:
                b_time = b_time.replace(tzinfo=timezone.utc)
            if abs((b_time - s_start).total_seconds()) < 1.0:
                is_booked = True
                break

        if not is_booked:
            available_slots.append({
                "doctor_id": doctor_id,
                "start_time": s_start.isoformat(),
                "end_time": s_end.isoformat(),
                "duration_minutes": settings.SLOT_DURATION_MINUTES
            })

    return available_slots
