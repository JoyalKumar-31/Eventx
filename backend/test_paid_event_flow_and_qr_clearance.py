"""
test_paid_event_flow_and_qr_clearance.py - Verification for Paid Event Payment Flow & QR Pass Clearance
Tests:
1. Register for free event via agent tool -> status is CONFIRMED, pass unlocked.
2. Register for paid event via agent tool -> status is PENDING_PAYMENT, pass locked.
3. Attempting to fetch QR pass for unpaid event returns HTTP 402.
4. Completing payment for paid event updates status to CONFIRMED and unlocks QR pass.
"""

import sys
import uuid
import requests
from pathlib import Path

# Add project root and backend to sys.path
root_dir = str(Path(__file__).resolve().parent.parent)
backend_dir = str(Path(__file__).resolve().parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

BASE_URL = "http://127.0.0.1:8000/api"

def run_tests():
    print("=" * 65)
    print("Beginning EventX Paid Event Payment Flow & QR Pass Verification")
    print("=" * 65)

    # 1. Login as Alex Sharma (Student)
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "alex.sharma@college.edu",
        "password": "Password123!"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    student = login_res.json()["user"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[AUTH PASS] Logged in as: {student['full_name']} (Role: {student['role']})")

    # 2. Test AI Agent tool: Free Event Registration
    print("\n--- Test 1: AI Agent Free Event Registration (Fee = 0) ---")
    from fest_agents.tools.team_tools import register_student_for_event, get_user_registrations
    from fest_agents.nodes import _generate_fallback

    # Create a fresh unique free event for test
    from app.db.session import SessionLocal
    from app.models.event import Event, EventCategory, Venue
    from app.models.registration import Registration
    from app.models.enums import EventStatus, RegistrationStatus
    import datetime

    db = SessionLocal()
    unique_suffix = uuid.uuid4().hex[:5].upper()
    cat = db.query(EventCategory).first()
    venue = db.query(Venue).first()
    
    free_event = Event(
        title=f"Open Source Hackathon {unique_suffix}",
        slug=f"open-source-hackathon-{unique_suffix.lower()}",
        description="Free hackathon for all fest participants.",
        category_id=cat.id,
        coordinator_id=2,
        venue_id=venue.id,
        registration_fee=0.0,
        max_participants=200,
        current_participants=0,
        status=EventStatus.PUBLISHED,
        registration_deadline=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10),
        start_time=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=12),
        end_time=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=12, hours=4),
        is_team_event=False
    )
    db.add(free_event)
    
    # Also create a fresh unique paid event
    paid_event = Event(
        title=f"RoboSumo Clash {unique_suffix}",
        slug=f"robo-sumo-clash-{unique_suffix.lower()}",
        description="Heavyweight battle bot showdown.",
        category_id=cat.id,
        coordinator_id=2,
        venue_id=venue.id,
        registration_fee=250.0,
        max_participants=50,
        current_participants=0,
        status=EventStatus.PUBLISHED,
        registration_deadline=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10),
        start_time=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=14),
        end_time=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=14, hours=4),
        is_team_event=False
    )
    db.add(paid_event)
    db.commit()
    db.refresh(free_event)
    db.refresh(paid_event)
    db.close()

    # Register for free event via agent tool
    free_reg_res = register_student_for_event(
        event_name_or_id=free_event.title,
        user_id=student["id"],
        user_email=student["email"]
    )
    assert free_reg_res["success"] is True, f"Free reg failed: {free_reg_res}"
    assert free_reg_res["status"] == "CONFIRMED", f"Expected CONFIRMED for free event, got {free_reg_res['status']}"
    assert "PASS-" in free_reg_res["qr_pass"], f"Expected active PASS- hash, got {free_reg_res['qr_pass']}"
    assert "Registration Confirmed" in free_reg_res["message"]
    print(f"[PASS 1] Free Event Registration Confirmed immediately: Status={free_reg_res['status']}, Pass={free_reg_res['qr_pass']}")

    # 3. Test AI Agent tool: Paid Event Registration (Fee > 0)
    print("\n--- Test 2: AI Agent Paid Event Registration (Fee > 0) ---")
    paid_reg_res = register_student_for_event(
        event_name_or_id=paid_event.title,
        user_id=student["id"],
        user_email=student["email"]
    )
    assert paid_reg_res["success"] is True, f"Paid reg failed: {paid_reg_res}"
    assert paid_reg_res["status"] == "PENDING_PAYMENT", f"Expected PENDING_PAYMENT, got {paid_reg_res['status']}"
    assert "Locked" in paid_reg_res["qr_pass"], f"Expected locked pass, got {paid_reg_res['qr_pass']}"
    assert "Locked" in paid_reg_res["message"]
    assert "My Registrations" in paid_reg_res["message"]
    print(f"[PASS 2] Paid Event Registration correctly in PENDING_PAYMENT: Status={paid_reg_res['status']}, Pass={paid_reg_res['qr_pass']}")

    # Verify get_user_registrations masks unpaid pass
    user_regs = get_user_registrations(user_id=student["id"])
    paid_found = [r for r in user_regs if r["registration_number"] == paid_reg_res["registration_number"]]
    assert len(paid_found) == 1, "Registration not found in get_user_registrations"
    assert "Locked" in paid_found[0]["qr_pass"], f"Expected pass to be masked as locked, got {paid_found[0]['qr_pass']}"
    print(f"[PASS 2.1] get_user_registrations masked unpaid pass as: {paid_found[0]['qr_pass']}")

    # 4. Test API Endpoint: Fetch QR pass for unpaid registration returns 402
    print("\n--- Test 3: Backend API HTTP 402 Enforcement on Unpaid Pass ---")
    db = SessionLocal()
    db_paid_reg = db.query(Registration).filter(Registration.registration_number == paid_reg_res["registration_number"]).first()
    paid_reg_id = db_paid_reg.id
    db.close()

    # Attempt to fetch pass
    pass_res = requests.get(f"{BASE_URL}/registrations/{paid_reg_id}/pass", headers=headers)
    assert pass_res.status_code == 402, f"Expected HTTP 402, got {pass_res.status_code}: {pass_res.text}"
    err_msg = pass_res.json().get("message") or pass_res.json().get("detail") or ""
    assert "Payment required" in err_msg, f"Unexpected error detail: {pass_res.json()}"
    print(f"[PASS 3] Fetching QR pass for unpaid registration returned HTTP 402: {err_msg}")

    # Also test Reg ID 3 (RoboWars Combat Championship)
    reg3_res = requests.get(f"{BASE_URL}/registrations/3/pass", headers=headers)
    assert reg3_res.status_code == 402, f"Expected Reg ID 3 to return 402, got {reg3_res.status_code}: {reg3_res.text}"
    reg3_msg = reg3_res.json().get("message") or reg3_res.json().get("detail") or ""
    assert "Payment required" in reg3_msg
    print(f"[PASS 3.1] Reg ID 3 (RoboWars Combat Championship) returned HTTP 402: {reg3_msg}")

    # 5. Test Payment Verification -> Unlocks QR pass & status becomes CONFIRMED
    print("\n--- Test 4: Complete Payment & Verify Pass Unlocking ---")
    # Create payment order
    order_res = requests.post(f"{BASE_URL}/payments/create-order", headers=headers, json={
        "registration_id": paid_reg_id
    })
    assert order_res.status_code == 201, f"Order creation failed: {order_res.text}"
    payment_id = order_res.json()["id"]
    print(f"[ORDER CREATED] Payment ID={payment_id}, Amount=₹{order_res.json()['amount']}")

    # Verify payment (Simulate success)
    verify_res = requests.post(f"{BASE_URL}/payments/verify", headers=headers, json={
        "payment_id": payment_id,
        "transaction_id": f"TXN_{uuid.uuid4().hex[:10].upper()}",
        "payment_method": "UPI",
        "simulate_status": "SUCCESS"
    })
    assert verify_res.status_code == 200, f"Payment verify failed: {verify_res.text}"
    assert verify_res.json()["status"] == "SUCCESS", f"Expected SUCCESS, got {verify_res.json()['status']}"
    print(f"[PAYMENT SUCCESS] Payment marked SUCCESS, Invoice={verify_res.json().get('invoice', {}).get('invoice_number')}")

    # Now fetch registration details
    my_regs_res = requests.get(f"{BASE_URL}/registrations/my", headers=headers)
    assert my_regs_res.status_code == 200
    my_paid_reg = [r for r in my_regs_res.json() if r["id"] == paid_reg_id][0]
    assert my_paid_reg["status"] == "CONFIRMED", f"Expected CONFIRMED post-payment, got {my_paid_reg['status']}"
    assert my_paid_reg["payment_status"] == "SUCCESS", f"Expected payment_status SUCCESS, got {my_paid_reg['payment_status']}"
    print(f"[REG CONFIRMED] Registration status transitioned to: {my_paid_reg['status']}, Payment: {my_paid_reg['payment_status']}")

    # Now attempt to fetch QR pass -> must succeed with 200 OK
    unlocked_pass_res = requests.get(f"{BASE_URL}/registrations/{paid_reg_id}/pass", headers=headers)
    assert unlocked_pass_res.status_code == 200, f"Expected 200 OK after payment, got {unlocked_pass_res.status_code}: {unlocked_pass_res.text}"
    pass_data = unlocked_pass_res.json()
    assert pass_data["qr_image_base64"].startswith("data:image/png;base64,"), "QR image base64 missing"
    print(f"[PASS 4] QR Pass successfully UNLOCKED! QR image payload retrieved: {pass_data['qr_code_hash']}")

    # 6. Verify Free Event Pass: Algorithm Masters Sprint (ID 10)
    print("\n--- Test 5: Verify Free Event (Algorithm Masters Sprint) Pass ---")
    algo_reg_id = 10
    algo_pass_res = requests.get(f"{BASE_URL}/registrations/{algo_reg_id}/pass", headers=headers)
    assert algo_pass_res.status_code == 200, f"Algorithm Masters Sprint pass failed: {algo_pass_res.text}"
    print(f"[PASS 5] Algorithm Masters Sprint (Free Event) Entry Pass is active immediately: {algo_pass_res.json()['event_title']}")

    print("\n" + "=" * 65)
    print("ALL TESTS PASSED: Paid Event Payment Flow & QR Pass Clearance verified!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
