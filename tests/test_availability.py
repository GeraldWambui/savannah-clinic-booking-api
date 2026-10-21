from datetime import date, datetime, timedelta, timezone


def test_get_doctor_availability_weekday(client):
    # Friday 2026-10-23
    response = client.get("/doctors/11111111-1111-1111-1111-111111111111/availability?date=2026-10-23")
    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == "11111111-1111-1111-1111-111111111111"
    assert data["total_slots"] == 16
    assert len(data["available_slots"]) == 16


def test_get_doctor_availability_weekend_empty(client):
    # Sunday 2026-10-25
    response = client.get("/doctors/11111111-1111-1111-1111-111111111111/availability?date=2026-10-25")
    assert response.status_code == 200
    data = response.json()
    assert data["total_slots"] == 0
    assert len(data["available_slots"]) == 0


def test_availability_excludes_booked_slot_and_restores_on_cancel(client):
    doc_id = "11111111-1111-1111-1111-111111111111"
    pat_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    slot_time = "2026-10-23T06:30:00Z"

    # Initial availability: 16 slots
    res1 = client.get(f"/doctors/{doc_id}/availability?date=2026-10-23")
    assert res1.json()["total_slots"] == 16

    # Book the slot
    book_res = client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id,
        "start_time": slot_time
    })
    assert book_res.status_code == 201
    appt_id = book_res.json()["id"]

    # Availability must now be 15 slots and exclude 06:30
    res2 = client.get(f"/doctors/{doc_id}/availability?date=2026-10-23")
    assert res2.json()["total_slots"] == 15
    slot_starts = [s["start_time"] for s in res2.json()["available_slots"]]
    assert not any("06:30:00" in s for s in slot_starts)

    # Cancel the appointment
    cancel_res = client.patch(f"/appointments/{appt_id}/cancel", json={
        "reason": "Patient can no longer attend"
    })
    assert cancel_res.status_code == 200

    # Availability must restore back to 16 slots
    res3 = client.get(f"/doctors/{doc_id}/availability?date=2026-10-23")
    assert res3.json()["total_slots"] == 16


def test_doctor_not_found(client):
    response = client.get("/doctors/99999999-9999-9999-9999-999999999999/availability?date=2026-10-23")
    assert response.status_code == 404
    assert "not found" in response.json()["message"].lower()


def test_health_and_request_id_tracing(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert "x-request-id" in res.headers
    assert "x-process-time" in res.headers
    assert res.json()["status"] == "healthy"

