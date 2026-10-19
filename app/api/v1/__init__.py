"""API v1 router registry."""
from fastapi import APIRouter
from app.api.v1.doctors import router as doctors_router

api_router = APIRouter()
api_router.include_router(doctors_router, prefix="/doctors", tags=["Doctors & Availability"])
