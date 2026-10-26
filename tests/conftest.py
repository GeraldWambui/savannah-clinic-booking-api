import pytest
from datetime import time, datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

def get_test_future_dates():
    today = datetime.now(timezone.utc).date()
    days_to_add = (0 - today.weekday() + 7) % 7
    if days_to_add == 0:
        days_to_add = 7
    weekday = today + timedelta(days=days_to_add)
    weekend = weekday + timedelta(days=6)
    return weekday, weekend

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.doctor import Doctor
from app.models.schedule import DoctorWorkingHours
from app.models.patient import Patient

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


@pytest.fixture(scope="function")
def db():
    """Creates a fresh database schema for each test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    doc1 = Doctor(
        id="11111111-1111-1111-1111-111111111111",
        name="Dr. Test Sarah",
        email="dr.sarah@test.com",
        specialization="General Medicine",
        is_active=True
    )
    doc2 = Doctor(
        id="22222222-2222-2222-2222-222222222222",
        name="Dr. Test David",
        email="dr.david@test.com",
        specialization="Pediatrics",
        is_active=True
    )
    session.add_all([doc1, doc2])
    session.flush()

    for day in range(5):
        session.add(DoctorWorkingHours(
            doctor_id=doc1.id,
            day_of_week=day,
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_active=True
        ))
        session.add(DoctorWorkingHours(
            doctor_id=doc2.id,
            day_of_week=day,
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_active=True
        ))

    patient1 = Patient(
        id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        name="Test Patient Alice",
        email="alice@test.com",
        phone="+254711111111"
    )
    patient2 = Patient(
        id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        name="Test Patient Bob",
        email="bob@test.com",
        phone="+254722222222"
    )
    session.add_all([patient1, patient2])
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """TestClient that uses thread-safe database sessions."""
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

