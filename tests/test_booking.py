from datetime import datetime, timezone, timedelta
from tests.conftest import get_test_future_dates


def test_book_appointment_success(client):
    weekday, _ = get_test_future_dates()
    payload = {
        "doctor_id": "11111111-1111-1111-1111-111111111111",
        "patient_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "start_time": f"{weekday.isoformat()}T07:00:00Z"
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
    weekday, _ = get_test_future_dates()
    payload = {
        "doctor_id": "11111111-1111-1111-1111-111111111111",
        "patient_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "start_time": f"{weekday.isoformat()}T04:00:00Z"
    }
    response = client.post("/appointments", json=payload)
    assert response.status_code == 400
    assert "outside the doctor's working hours" in response.json()["message"].lower()


def test_book_appointment_invalid_boundary(client):
    weekday, _ = get_test_future_dates()
    payload = {
        "doctor_id": "11111111-1111-1111-1111-111111111111",
        "patient_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "start_time": f"{weekday.isoformat()}T07:15:00Z"
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
    weekday, _ = get_test_future_dates()
    date_str = weekday.isoformat()
    payload = {
        "doctor_id": "11111111-1111-1111-1111-111111111111",
        "patient_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "start_time": f"{date_str}T08:00:00Z"
    }
    res1 = client.post("/appointments", json=payload)
    assert res1.status_code == 201

    payload2 = {
        "doctor_id": "11111111-1111-1111-1111-111111111111",
        "patient_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "start_time": f"{date_str}T08:00:00Z"
    }
    res2 = client.post("/appointments", json=payload2)
    assert res2.status_code == 409
    assert "already taken" in res2.json()["message"].lower()


def test_cancel_appointment_lifecycle(client):
    weekday, _ = get_test_future_dates()
    book_res = client.post("/appointments", json={
        "doctor_id": "11111111-1111-1111-1111-111111111111",
        "patient_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "start_time": f"{weekday.isoformat()}T09:00:00Z"
    })
    assert book_res.status_code == 201
    appt_id = book_res.json()["id"]

    cancel_res = client.patch(f"/appointments/{appt_id}/cancel", json={
        "reason": "Recovered from illness"
    })
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"
    assert cancel_res.json()["cancellation_reason"] == "Recovered from illness"

    cancel_again = client.patch(f"/appointments/{appt_id}/cancel", json={
        "reason": "Trying to cancel again"
    })
    assert cancel_again.status_code == 400
    assert "already cancelled" in cancel_again.json()["message"].lower()


def test_reschedule_appointment_lifecycle(client):
    weekday, _ = get_test_future_dates()
    date_str = weekday.isoformat()
    doc_id = "11111111-1111-1111-1111-111111111111"
    pat_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    appt1 = client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id,
        "start_time": f"{date_str}T10:00:00Z"
    }).json()

    appt2 = client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "start_time": f"{date_str}T10:30:00Z"
    }).json()

    conflict_res = client.patch(f"/appointments/{appt1['id']}/reschedule", json={
        "new_start_time": f"{date_str}T10:30:00Z"
    })
    assert conflict_res.status_code == 409

    success_res = client.patch(f"/appointments/{appt1['id']}/reschedule", json={
        "new_start_time": f"{date_str}T11:00:00Z"
    })
    assert success_res.status_code == 200
    assert "11:00:00" in success_res.json()["start_time"]

    reuse_res = client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "start_time": f"{date_str}T10:00:00Z"
    })
    assert reuse_res.status_code == 201


def test_patient_upcoming_appointments_bonus(client):
    weekday, _ = get_test_future_dates()
    date_str = weekday.isoformat()
    doc_id = "11111111-1111-1111-1111-111111111111"
    pat_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id,
        "start_time": f"{date_str}T12:00:00Z"
    })
    client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id,
        "start_time": f"{date_str}T06:00:00Z"
    })

    res = client.get(f"/patients/{pat_id}/appointments")
    assert res.status_code == 200
    data = res.json()
    assert data["total_upcoming"] >= 2
    dates = [a["start_time"] for a in data["appointments"]]
    assert dates == sorted(dates)
