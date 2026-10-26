from datetime import date, datetime, timedelta, timezone
from tests.conftest import get_test_future_dates


def test_get_doctor_availability_weekday(client):
    weekday, _ = get_test_future_dates()
    response = client.get(f"/doctors/11111111-1111-1111-1111-111111111111/availability?date={weekday.isoformat()}")
    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == "11111111-1111-1111-1111-111111111111"
    assert data["total_slots"] == 16
    assert len(data["available_slots"]) == 16


def test_get_doctor_availability_weekend_empty(client):
    _, weekend = get_test_future_dates()
    response = client.get(f"/doctors/11111111-1111-1111-1111-111111111111/availability?date={weekend.isoformat()}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_slots"] == 0
    assert len(data["available_slots"]) == 0


def test_availability_excludes_booked_slot_and_restores_on_cancel(client):
    weekday, _ = get_test_future_dates()
    date_str = weekday.isoformat()
    doc_id = "11111111-1111-1111-1111-111111111111"
    pat_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    slot_time = f"{date_str}T06:30:00Z"

    res1 = client.get(f"/doctors/{doc_id}/availability?date={date_str}")
    assert res1.json()["total_slots"] == 16

    book_res = client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id,
        "start_time": slot_time
    })
    assert book_res.status_code == 201
    appt_id = book_res.json()["id"]

    res2 = client.get(f"/doctors/{doc_id}/availability?date={date_str}")
    assert res2.json()["total_slots"] == 15
    slot_starts = [s["start_time"] for s in res2.json()["available_slots"]]
    assert not any("06:30:00" in s for s in slot_starts)

    cancel_res = client.patch(f"/appointments/{appt_id}/cancel", json={
        "reason": "Patient can no longer attend"
    })
    assert cancel_res.status_code == 200

    res3 = client.get(f"/doctors/{doc_id}/availability?date={date_str}")
    assert res3.json()["total_slots"] == 16


def test_doctor_not_found(client):
    weekday, _ = get_test_future_dates()
    response = client.get(f"/doctors/99999999-9999-9999-9999-999999999999/availability?date={weekday.isoformat()}")
    assert response.status_code == 404
    assert "not found" in response.json()["message"].lower()


def test_health_and_request_id_tracing(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert "x-request-id" in res.headers
    assert "x-process-time" in res.headers
    assert res.json()["status"] == "healthy"

