from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.exceptions import (
    DoctorNotFoundException,
    PatientNotFoundException,
    AppointmentNotFoundException,
    SlotConflictException,
    SlotInPastException,
    BookingLeadTimeException,
    InvalidSlotBoundaryException,
    SlotOutsideWorkingHoursException,
    DoctorNotWorkingOnDayException,
    AppointmentAlreadyCancelledException,
    CannotRescheduleCancelledException,
)
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.schedule import DoctorWorkingHours
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.db.base import utc_now


def get_clinic_timezone() -> ZoneInfo:
    return ZoneInfo(settings.CLINIC_TIMEZONE)


def validate_slot_timing(start_time: datetime, now_utc: datetime = None) -> datetime:
    """Validates boundary alignment, past date, and 1-hour lead time.
    Returns normalized UTC datetime.
    """
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    else:
        start_time = start_time.astimezone(timezone.utc)

    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    if start_time.minute not in (0, 30) or start_time.second != 0 or start_time.microsecond != 0:
        raise InvalidSlotBoundaryException()

    if start_time <= now_utc:
        raise SlotInPastException()

    min_allowed = now_utc + timedelta(hours=settings.MIN_BOOKING_LEAD_HOURS)
    if start_time < min_allowed:
        raise BookingLeadTimeException()

    return start_time


def validate_doctor_schedule(db: Session, doctor_id: str, start_time_utc: datetime) -> tuple[datetime, datetime]:
    """Validates that a slot falls within the doctor's active working hours.
    Returns (start_time_utc, end_time_utc).
    """
    doctor = db.get(Doctor, doctor_id)
    if not doctor or not doctor.is_active:
        raise DoctorNotFoundException(doctor_id)

    clinic_tz = get_clinic_timezone()
    local_start = start_time_utc.astimezone(clinic_tz)
    local_end = (start_time_utc + timedelta(minutes=settings.SLOT_DURATION_MINUTES)).astimezone(clinic_tz)

    day_of_week = local_start.weekday()

    stmt = select(DoctorWorkingHours).where(
        DoctorWorkingHours.doctor_id == doctor_id,
        DoctorWorkingHours.day_of_week == day_of_week,
        DoctorWorkingHours.is_active.is_(True)
    )
    wh = db.scalars(stmt).first()
    if not wh:
        raise DoctorNotWorkingOnDayException()

    if local_start.time() < wh.start_time or local_end.time() > wh.end_time:
        raise SlotOutsideWorkingHoursException()

    end_time_utc = start_time_utc + timedelta(minutes=settings.SLOT_DURATION_MINUTES)
    return start_time_utc, end_time_utc


def book_appointment(
    db: Session,
    doctor_id: str,
    patient_id: str,
    start_time: datetime,
    now_utc: datetime = None
) -> Appointment:
    """Creates a new appointment with full validation and race-condition safety."""
    patient = db.get(Patient, patient_id)
    if not patient:
        raise PatientNotFoundException(patient_id)

    norm_start_utc = validate_slot_timing(start_time, now_utc=now_utc)
    norm_start_utc, norm_end_utc = validate_doctor_schedule(db, doctor_id, norm_start_utc)

    stmt_conflict = select(Appointment).where(
        and_(
            Appointment.doctor_id == doctor_id,
            Appointment.start_time == norm_start_utc,
            Appointment.status == AppointmentStatus.SCHEDULED.value
        )
    )
    existing = db.scalars(stmt_conflict).first()
    if existing:
        raise SlotConflictException()

    appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        start_time=norm_start_utc,
        end_time=norm_end_utc,
        status=AppointmentStatus.SCHEDULED.value
    )

    try:
        db.add(appointment)
        db.commit()
        return appointment
    except IntegrityError:
        db.rollback()
        raise SlotConflictException()


def cancel_appointment(
    db: Session,
    appointment_id: str,
    reason: str
) -> Appointment:
    """Cancels an existing appointment. Slot automatically becomes bookable again."""
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise AppointmentNotFoundException(appointment_id)

    if appointment.status == AppointmentStatus.CANCELLED.value:
        raise AppointmentAlreadyCancelledException()

    appointment.status = AppointmentStatus.CANCELLED.value
    appointment.cancellation_reason = reason.strip()
    appointment.cancelled_at = utc_now()

    db.commit()
    return appointment


def reschedule_appointment(
    db: Session,
    appointment_id: str,
    new_start_time: datetime,
    now_utc: datetime = None
) -> Appointment:
    """Atomically moves an appointment to a new slot.
    Rolls back cleanly if the new slot is unavailable, preserving the original booking.
    """
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise AppointmentNotFoundException(appointment_id)

    if appointment.status == AppointmentStatus.CANCELLED.value:
        raise CannotRescheduleCancelledException()

    norm_start_utc = validate_slot_timing(new_start_time, now_utc=now_utc)
    norm_start_utc, norm_end_utc = validate_doctor_schedule(db, appointment.doctor_id, norm_start_utc)

    if appointment.start_time == norm_start_utc:
        return appointment

    stmt_conflict = select(Appointment).where(
        and_(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.start_time == norm_start_utc,
            Appointment.status == AppointmentStatus.SCHEDULED.value,
            Appointment.id != appointment_id
        )
    )
    if db.scalars(stmt_conflict).first():
        raise SlotConflictException()

    try:
        appointment.start_time = norm_start_utc
        appointment.end_time = norm_end_utc
        db.commit()
        return appointment
    except IntegrityError:
        db.rollback()
        raise SlotConflictException()
