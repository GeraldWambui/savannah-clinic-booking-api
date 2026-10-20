from datetime import datetime, timezone, timedelta


def test_book_appointment_success(client):
    payload = {
        "doctor_id": "11111111-1111-1111-1111-111111111111",
        "patient_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "start_time": "2026-10-23T07:00:00Z"
    }
    response = client.post("/appointments", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["doctor_id"] == payload["doctor_id"]
    assert data["patient_id"] == payload["patient_id"]
    assert data["status"] == "SCHEDULED"
    assert "07:00:00" in data["start_time"]
    assert "07:30:00" in data["end_time"]


def test_book_appointment_outside_working_hours(client):
    # 04:00 UTC = 07:00 EAT (Doctor starts at 09:00 EAT)
    payload = {
        "doctor_id": "11111111-1111-1111-1111-111111111111",
        "patient_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "start_time": "2026-10-23T04:00:00Z"
    }
    response = client.post("/appointments", json=payload)
    assert response.status_code == 400
    assert "outside the doctor's working hours" in response.json()["message"].lower()


def test_book_appointment_invalid_boundary(client):
    # 07:15 is not a 30-min boundary (:00 or :30)
    payload = {
        "doctor_id": "11111111-1111-1111-1111-111111111111",
        "patient_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "start_time": "2026-10-23T07:15:00Z"
    }
    response = client.post("/appointments", json=payload)
    assert response.status_code == 400
    assert "30-minute" in response.json()["message"].lower()


def test_book_appointment_in_the_past(client):
    payload = {
        "doctor_id": "11111111-1111-1111-1111-111111111111",
        "patient_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "start_time": "2020-01-01T07:00:00Z"
    }
    response = client.post("/appointments", json=payload)
    assert response.status_code == 400
    assert "past" in response.json()["message"].lower()


def test_book_appointment_duplicate_returns_409(client):
    payload = {
        "doctor_id": "11111111-1111-1111-1111-111111111111",
        "patient_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "start_time": "2026-10-23T08:00:00Z"
    }
    res1 = client.post("/appointments", json=payload)
    assert res1.status_code == 201

    # Second patient attempts to book same doctor and slot
    payload2 = {
        "doctor_id": "11111111-1111-1111-1111-111111111111",
        "patient_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "start_time": "2026-10-23T08:00:00Z"
    }
    res2 = client.post("/appointments", json=payload2)
    assert res2.status_code == 409
    assert "already taken" in res2.json()["message"].lower()


def test_cancel_appointment_lifecycle(client):
    book_res = client.post("/appointments", json={
        "doctor_id": "11111111-1111-1111-1111-111111111111",
        "patient_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "start_time": "2026-10-23T09:00:00Z"
    })
    assert book_res.status_code == 201
    appt_id = book_res.json()["id"]

    # Cancel with reason
    cancel_res = client.patch(f"/appointments/{appt_id}/cancel", json={
        "reason": "Recovered from illness"
    })
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"
    assert cancel_res.json()["cancellation_reason"] == "Recovered from illness"

    # Cancelling again returns 400
    cancel_again = client.patch(f"/appointments/{appt_id}/cancel", json={
        "reason": "Trying to cancel again"
    })
    assert cancel_again.status_code == 400
    assert "already cancelled" in cancel_again.json()["message"].lower()


def test_reschedule_appointment_lifecycle(client):
    doc_id = "11111111-1111-1111-1111-111111111111"
    pat_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    # 1. Book first appointment at 10:00 UTC
    appt1 = client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id,
        "start_time": "2026-10-23T10:00:00Z"
    }).json()

    # 2. Book second appointment at 10:30 UTC
    appt2 = client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "start_time": "2026-10-23T10:30:00Z"
    }).json()

    # 3. Try to reschedule appt1 into appt2's slot (should fail with 409)
    conflict_res = client.patch(f"/appointments/{appt1['id']}/reschedule", json={
        "new_start_time": "2026-10-23T10:30:00Z"
    })
    assert conflict_res.status_code == 409

    # 4. Reschedule appt1 into a free slot (11:00 UTC)
    success_res = client.patch(f"/appointments/{appt1['id']}/reschedule", json={
        "new_start_time": "2026-10-23T11:00:00Z"
    })
    assert success_res.status_code == 200
    assert "11:00:00" in success_res.json()["start_time"]

    # 5. Original slot (10:00 UTC) is now free; another patient can book it!
    reuse_res = client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "start_time": "2026-10-23T10:00:00Z"
    })
    assert reuse_res.status_code == 201


def test_patient_upcoming_appointments_bonus(client):
    doc_id = "11111111-1111-1111-1111-111111111111"
    pat_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    # Book two upcoming appointments on different dates
    client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id,
        "start_time": "2026-10-23T12:00:00Z"
    })
    client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id,
        "start_time": "2026-10-23T06:00:00Z"
    })

    # Fetch patient upcoming appointments
    res = client.get(f"/patients/{pat_id}/appointments")
    assert res.status_code == 200
    data = res.json()
    assert data["total_upcoming"] >= 2
    # Verify sorted chronologically ASC
    dates = [a["start_time"] for a in data["appointments"]]
    assert dates == sorted(dates)
