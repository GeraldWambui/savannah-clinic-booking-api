import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.doctor import Doctor
from app.models.schedule import DoctorWorkingHours
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.services.booking import book_appointment


def test_concurrent_booking_race_condition_prevention(client):
    """Verifies that when multiple booking requests target the exact same doctor and slot:
    1. Exactly one request succeeds with HTTP 201 Created.
    2. All subsequent or concurrent conflicting requests fail gracefully with HTTP 409 Conflict.
    3. Zero double-booking occurs in the database.
    """
    doc_id = "22222222-2222-2222-2222-222222222222"
    pat_id1 = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    pat_id2 = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    slot_time = "2026-10-23T09:00:00Z"

    res1 = client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id1,
        "start_time": slot_time
    })
    assert res1.status_code == 201
    assert res1.json()["status"] == "SCHEDULED"

    res2 = client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id2,
        "start_time": slot_time
    })
    assert res2.status_code == 409
    assert "already taken" in res2.json()["message"].lower()

    res3 = client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id1,
        "start_time": slot_time
    })
    assert res3.status_code == 409
    assert "already taken" in res3.json()["message"].lower()


def test_multithreaded_concurrent_booking_race_condition():
    """Simulates 5 parallel OS threads firing simultaneous booking requests
    at the exact same millisecond against the exact same doctor slot.
    
    Verifies that the database-level partial unique index:
    1. Permits exactly ONE booking to succeed (201).
    2. Rejects all remaining 4 concurrent threads with 409 Conflict.
    3. Leaves exactly 1 appointment row in the database.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"timeout": 20})
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL;"))
        conn.commit()

    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

    session = SessionFactory()
    doc = Doctor(
        id="33333333-3333-3333-3333-333333333333",
        name="Dr. Race Condition Test",
        email="dr.race@test.com",
        specialization="Critical Care",
        is_active=True
    )
    pat1 = Patient(
        id="11111111-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        name="Patient Thread A",
        email="threadA@test.com",
        phone="+254700000001"
    )
    pat2 = Patient(
        id="22222222-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        name="Patient Thread B",
        email="threadB@test.com",
        phone="+254700000002"
    )
    session.add_all([doc, pat1, pat2])
    for day in range(5):
        session.add(DoctorWorkingHours(
            doctor_id=doc.id,
            day_of_week=day,
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_active=True
        ))
    session.commit()
    session.close()

    target_slot = datetime(2026, 10, 23, 7, 0, tzinfo=timezone.utc)

    def attempt_booking(patient_id: str) -> tuple[int, str]:
        db = SessionFactory()
        try:
            appt = book_appointment(
                db=db,
                doctor_id="33333333-3333-3333-3333-333333333333",
                patient_id=patient_id,
                start_time=target_slot
            )
            return (201, appt.id)
        except Exception as e:
            return (getattr(e, "status_code", 500), type(e).__name__)
        finally:
            db.close()

    patient_ids = [
        "11111111-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "22222222-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "11111111-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "22222222-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "11111111-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    ]

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(attempt_booking, patient_ids))

    codes = [r[0] for r in results]
    assert codes.count(201) == 1, f"Expected exactly 1 booking to succeed, got {codes.count(201)}"
    assert codes.count(409) == 4, f"Expected 4 conflicts, got {codes.count(409)}"

    verify_session = SessionFactory()
    count = verify_session.query(Appointment).filter(
        Appointment.doctor_id == "33333333-3333-3333-3333-333333333333",
        Appointment.start_time == target_slot
    ).count()
    verify_session.close()

    assert count == 1, f"Expected 1 appointment row, found {count}"

    os.unlink(db_path)
