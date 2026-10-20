from fastapi import APIRouter
from app.api.v1.doctors import router as doctors_router
from app.api.v1.appointments import router as appointments_router

api_router = APIRouter()
api_router.include_router(doctors_router, prefix="/doctors", tags=["Doctors & Availability"])
api_router.include_router(appointments_router, prefix="/appointments", tags=["Appointments"])

