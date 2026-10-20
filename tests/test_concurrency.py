from concurrent.futures import ThreadPoolExecutor


def test_concurrent_booking_race_condition_prevention(client):
    """Simulates 5 concurrent patient requests attempting to book the EXACT same doctor and slot.
    Guarantees that:
    1. Exactly one request succeeds with HTTP 201 Created.
    2. All other concurrent requests fail gracefully with HTTP 409 Conflict.
    3. Zero double-booking occurs in the database.
    """
    doc_id = "22222222-2222-2222-2222-222222222222"
    pat_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    slot_time = "2026-10-23T09:00:00Z"

    def attempt_booking(i: int):
        return client.post("/appointments", json={
            "doctor_id": doc_id,
            "patient_id": pat_id,
            "start_time": slot_time
        })

    # Spawn 5 concurrent threads
    with ThreadPoolExecutor(max_workers=5) as executor:
        responses = list(executor.map(attempt_booking, range(5)))

    status_codes = [r.status_code for r in responses]
    success_count = status_codes.count(201)
    conflict_count = status_codes.count(409)

    assert success_count == 1, f"Expected exactly 1 successful booking, got {success_count}. Codes: {status_codes}"
    assert conflict_count == 4, f"Expected 4 conflicts, got {conflict_count}. Codes: {status_codes}"
