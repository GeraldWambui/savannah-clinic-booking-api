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

    # First booking claims the slot
    res1 = client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id1,
        "start_time": slot_time
    })
    assert res1.status_code == 201
    assert res1.json()["status"] == "SCHEDULED"

    # Conflicting booking attempt 1 for the same doctor and slot
    res2 = client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id2,
        "start_time": slot_time
    })
    assert res2.status_code == 409
    assert "already taken" in res2.json()["message"].lower()

    # Conflicting booking attempt 2 for the same doctor and slot
    res3 = client.post("/appointments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id1,
        "start_time": slot_time
    })
    assert res3.status_code == 409
    assert "already taken" in res3.json()["message"].lower()
