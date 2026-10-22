"""Seed script to populate the database with initial clinic data:
- 5 Doctors with standard clinical working hours (Monday-Friday 09:00 - 17:00)
- Sample Patients
"""
import sys
import os
from datetime import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.doctor import Doctor
from app.models.schedule import DoctorWorkingHours
from app.models.patient import Patient


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(Doctor).count() > 0:
            print("Database already contains doctor records. Skipping seed.")
            return

        print("Seeding initial clinic data (5 Doctors + Working Hours)...")

        doctors_data = [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "name": "Dr. Sarah Kimani",
                "email": "sarah.kimani@savannahclinic.com",
                "specialization": "General Practitioner",
            },
            {
                "id": "22222222-2222-2222-2222-222222222222",
                "name": "Dr. David Ochieng",
                "email": "david.ochieng@savannahclinic.com",
                "specialization": "Pediatrician",
            },
            {
                "id": "33333333-3333-3333-3333-333333333333",
                "name": "Dr. Amina Mohamed",
                "email": "amina.mohamed@savannahclinic.com",
                "specialization": "Cardiologist",
            },
            {
                "id": "44444444-4444-4444-4444-444444444444",
                "name": "Dr. Peter Kamau",
                "email": "peter.kamau@savannahclinic.com",
                "specialization": "Dermatologist",
            },
            {
                "id": "55555555-5555-5555-5555-555555555555",
                "name": "Dr. Grace Mwangi",
                "email": "grace.mwangi@savannahclinic.com",
                "specialization": "Orthopedic Surgeon",
            },
        ]

        for doc_info in doctors_data:
            doctor = Doctor(**doc_info)
            db.add(doctor)
            db.flush()

            for day_idx in range(5):
                wh = DoctorWorkingHours(
                    doctor_id=doctor.id,
                    day_of_week=day_idx,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    is_active=True
                )
                db.add(wh)

        patients_data = [
            {
                "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+254712345678",
            },
            {
                "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                "name": "Jane Wanjiku",
                "email": "jane.wanjiku@example.com",
                "phone": "+254798765432",
            }
        ]
        for pat_info in patients_data:
            patient = Patient(**pat_info)
            db.add(patient)

        db.commit()
        print("Database successfully seeded with 5 doctors and 2 sample patients!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
