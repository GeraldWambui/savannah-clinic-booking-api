from fastapi import Request, status
from fastapi.responses import JSONResponse


class ClinicException(Exception):
    """Base domain exception."""
    status_code: int = status.HTTP_400_BAD_REQUEST
    detail: str = "A clinic domain error occurred."

    def __init__(self, detail: str = None, status_code: int = None):
        if detail:
            self.detail = detail
        if status_code:
            self.status_code = status_code
        super().__init__(self.detail)


class ResourceNotFoundException(ClinicException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Requested resource was not found."


class DoctorNotFoundException(ResourceNotFoundException):
    def __init__(self, doctor_id: str):
        super().__init__(f"Doctor with ID '{doctor_id}' was not found.")


class PatientNotFoundException(ResourceNotFoundException):
    def __init__(self, patient_id: str):
        super().__init__(f"Patient with ID '{patient_id}' was not found.")


class AppointmentNotFoundException(ResourceNotFoundException):
    def __init__(self, appointment_id: str):
        super().__init__(f"Appointment with ID '{appointment_id}' was not found.")


class SlotConflictException(ClinicException):
    status_code = status.HTTP_409_CONFLICT
    detail = "The requested appointment slot is already taken."


class SlotInPastException(ClinicException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Appointment slot cannot be in the past."


class BookingLeadTimeException(ClinicException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Appointments must be booked at least 1 hour in advance."


class InvalidSlotBoundaryException(ClinicException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Appointment times must align strictly with 30-minute boundaries (minute :00 or :30)."


class SlotOutsideWorkingHoursException(ClinicException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Requested slot is outside the doctor's working hours."


class DoctorNotWorkingOnDayException(ClinicException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Doctor does not have scheduled working hours on this day."


class AppointmentAlreadyCancelledException(ClinicException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Appointment is already cancelled."


class CannotRescheduleCancelledException(ClinicException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Cannot reschedule an appointment that has already been cancelled."


async def clinic_exception_handler(request: Request, exc: ClinicException) -> JSONResponse:
    """Standardized error envelope for domain exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )
