from datetime import datetime, timezone, timedelta
from tests.test_events_and_media import get_token


def test_full_fest_workflow(client):
    admin_token = get_token(client, "admin_flow@fest.edu", "Pass1234!", "ADMIN", "Administrator")
    coord_token = get_token(client, "coord_flow@fest.edu", "Pass1234!", "EVENT_COORDINATOR", "Coordinator")
    judge_token = get_token(client, "judge_flow@fest.edu", "Pass1234!", "JUDGE", "Dr. Judge")
    student_token = get_token(client, "student_flow@fest.edu", "Pass1234!", "STUDENT", "Student Participant")

    # 1. Category
    cat_id = client.post("/api/events/categories", json={
        "name": "Robotics", "description": "Battle of Bots"
    }, headers={"Authorization": f"Bearer {admin_token}"}).json()["id"]

    # 2. Event
    now = datetime.now(timezone.utc)
    event_id = client.post("/api/events", json={
        "title": "RoboWars 2026",
        "description": "Combat robotics competition",
        "category_id": cat_id,
        "start_time": (now + timedelta(days=2)).isoformat(),
        "end_time": (now + timedelta(days=3)).isoformat(),
        "registration_deadline": (now + timedelta(days=1)).isoformat(),
        "max_participants": 20,
        "registration_fee": 150.0,
        "is_team_event": False
    }, headers={"Authorization": f"Bearer {coord_token}"}).json()["id"]

    client.post(f"/api/events/{event_id}/publish", headers={"Authorization": f"Bearer {coord_token}"})

    # 3. Student registers
    reg_res = client.post("/api/registrations", json={"event_id": event_id}, headers={"Authorization": f"Bearer {student_token}"})
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    reg_id = reg_data["id"]
    assert reg_data["status"] == "PENDING_PAYMENT"

    # 4. Payment order & verification
    order_res = client.post("/api/payments/create-order", json={"registration_id": reg_id}, headers={"Authorization": f"Bearer {student_token}"})
    assert order_res.status_code == 201
    pay_id = order_res.json()["id"]

    verify_res = client.post("/api/payments/verify", json={
        "payment_id": pay_id,
        "transaction_id": "TXN_ROBO_998877",
        "payment_method": "UPI",
        "simulate_status": "SUCCESS"
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "SUCCESS"
    assert verify_res.json()["invoice"] is not None

    # 5. Student gets QR entry pass
    pass_res = client.get(f"/api/registrations/{reg_id}/pass", headers={"Authorization": f"Bearer {student_token}"})
    assert pass_res.status_code == 200
    qr_payload = pass_res.json()["qr_code_hash"]
    assert pass_res.json()["qr_image_base64"].startswith("data:image/png;base64,")

    # 6. Coordinator scans QR ticket
    scan_res = client.post("/api/attendance/scan", json={
        "qr_payload": qr_payload,
        "event_id": event_id
    }, headers={"Authorization": f"Bearer {coord_token}"})
    assert scan_res.status_code == 200
    assert scan_res.json()["entry_status"] == "VALID"

    # 7. Duplicate scan attempt -> 409 Conflict
    dup_scan_res = client.post("/api/attendance/scan", json={
        "qr_payload": qr_payload,
        "event_id": event_id
    }, headers={"Authorization": f"Bearer {coord_token}"})
    assert dup_scan_res.status_code == 409
    assert dup_scan_res.json()["error_code"] == "DUPLICATE_ENTRY"

    # 8. Coordinator assigns judge
    # Get Judge user id
    judge_info = client.get("/api/auth/me", headers={"Authorization": f"Bearer {judge_token}"}).json()
    judge_id = judge_info["id"]

    assign_res = client.post("/api/judges/assign", json={
        "event_id": event_id,
        "judge_id": judge_id
    }, headers={"Authorization": f"Bearer {coord_token}"})
    assert assign_res.status_code == 201

    # 9. Coordinator sets scoring criteria
    crit_res = client.post("/api/judges/criteria", json={
        "event_id": event_id,
        "name": "Mechanical Robustness",
        "description": "Armor durability and construction",
        "max_score": 50.0,
        "weightage": 1.0
    }, headers={"Authorization": f"Bearer {coord_token}"})
    assert crit_res.status_code == 201
    crit_id = crit_res.json()["id"]

    # 10. Judge submits score
    score_res = client.post(f"/api/scores/event/{event_id}", json={
        "registration_id": reg_id,
        "scores": [
            {"criteria_id": crit_id, "score_value": 45.0, "remarks": "Excellent build quality"}
        ]
    }, headers={"Authorization": f"Bearer {judge_token}"})
    assert score_res.status_code == 200

    # 11. Coordinator publishes results
    pub_res = client.post(f"/api/results/publish/{event_id}", headers={"Authorization": f"Bearer {coord_token}"})
    assert pub_res.status_code == 200
    results = pub_res.json()
    assert len(results) == 1
    assert results[0]["rank"] == 1

    # 12. Student gets generated certificate
    my_certs = client.get("/api/certificates/my", headers={"Authorization": f"Bearer {student_token}"})
    assert my_certs.status_code == 200
    certs = my_certs.json()
    assert len(certs) == 1
    cert_id = certs[0]["id"]
    cert_hash = certs[0]["verification_hash"]

    # 13. Download dynamic PDF certificate
    pdf_res = client.get(f"/api/certificates/{cert_id}/download", headers={"Authorization": f"Bearer {student_token}"})
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000  # Non-empty valid PDF

    # 14. Public verification
    verify_cert = client.get(f"/api/certificates/verify/{cert_hash}")
    assert verify_cert.status_code == 200
    assert verify_cert.json()["is_valid"] is True
    assert verify_cert.json()["event_title"] == "RoboWars 2026"
