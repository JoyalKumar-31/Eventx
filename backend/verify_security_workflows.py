import sys
import requests
import uuid
import time

BASE_URL = "http://127.0.0.1:8000/api"

def print_test(name):
    print(f"\n=======================================================")
    print(f"RUNNING TEST: {name}")
    print(f"=======================================================")

def assert_true(condition, msg):
    if not condition:
        print(f"❌ FAILED: {msg}")
        sys.exit(1)
    else:
        print(f"✅ PASSED: {msg}")

def main():
    print("Beginning EventX End-to-End Security Verification...")

    # 0. Authenticate as Admin
    print_test("0. Authenticate as Fest Administrator")
    admin_login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@college.edu",
        "password": "password123"
    })
    assert_true(admin_login_res.status_code == 200, "Admin credentials accepted")
    admin_data = admin_login_res.json()
    admin_token = admin_data["access_token"]
    assert_true(admin_data["user"]["role"] == "ADMIN", "Admin role confirmed")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Public Registration Role Tampering Test
    print_test("1. Public Registration Role Tampering Resistance")
    rand_id = uuid.uuid4().hex[:6]
    tamper_email = f"tamper_{rand_id}@test.com"
    tamper_payload = {
        "email": tamper_email,
        "password": "password123",
        "full_name": "Role Poisoning Attacker",
        "role": "ADMIN",  # ATTACK: Attempting privilege escalation to ADMIN
        "college_name": "Test University",
        "student_id_number": f"TAMPER-{rand_id}",
        "department": "Security",
        "year_of_study": "4th Year"
    }
    reg_res = requests.post(f"{BASE_URL}/auth/register", json=tamper_payload)
    assert_true(reg_res.status_code in [200, 201], f"Registration response code 200/201: {reg_res.status_code}")
    reg_data = reg_res.json()
    assert_true(reg_data["role"] == "STUDENT", f"Injected role 'ADMIN' was strictly disregarded and set to STUDENT: {reg_data['role']}")

    # Login as this newly registered user and verify JWT role claim
    tamper_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": tamper_email,
        "password": "password123"
    })
    tamper_user = tamper_login.json()["user"]
    tamper_token = tamper_login.json()["access_token"]
    assert_true(tamper_user["role"] == "STUDENT", f"JWT and Database role is strictly STUDENT: {tamper_user['role']}")

    # Verify that this user cannot access Admin endpoints
    tamper_admin_access = requests.get(
        f"{BASE_URL}/admin/applications/coordinators",
        headers={"Authorization": f"Bearer {tamper_token}"}
    )
    assert_true(tamper_admin_access.status_code == 403, f"Student is denied Admin endpoints (403 Forbidden): {tamper_admin_access.status_code}")

    # 2. Coordinator Application and Approval Workflow
    print_test("2. Event Coordinator Application and Approval Workflow")
    coord_email = f"coord_{rand_id}@univ.edu"
    coord_payload = {
        "full_name": f"Prof. Coordinate {rand_id}",
        "email": coord_email,
        "password": "password123",
        "phone": "+91 9999888877",
        "department": "Computer Science",
        "designation": "Associate Coordinator",
        "experience": "Organized 3 hackathons and 2 tech symposia.",
        "office_location": "CS Dept Room 404"
    }

    # Submit application
    app_res = requests.post(f"{BASE_URL}/auth/apply/coordinator", json=coord_payload)
    assert_true(app_res.status_code in [200, 201], f"Application submitted: {app_res.status_code}")
    app_data = app_res.json()
    app_id = app_data["id"]
    assert_true(app_data["status"] == "PENDING", f"Application created with PENDING status: {app_data['status']}")

    # Candidate logs in - role must still be STUDENT (not Coordinator)
    coord_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": coord_email,
        "password": "password123"
    })
    coord_token_initial = coord_login.json()["access_token"]
    assert_true(coord_login.json()["user"]["role"] == "STUDENT", "Unapproved coordinator has only STUDENT privileges")

    # Verify coordinator public status lookup
    status_res = requests.get(f"{BASE_URL}/auth/application/status", params={"email": coord_email})
    assert_true(status_res.status_code == 200, "Candidate can query their pending status")
    assert_true(status_res.json()["coordinator_application"]["status"] == "PENDING", "Status lookup confirms PENDING")

    # Admin reviews and approves the application
    approve_res = requests.post(
        f"{BASE_URL}/admin/applications/coordinators/{app_id}/approve",
        headers=admin_headers,
        json={"admin_notes": "Verified credentials with CS Faculty Head."}
    )
    assert_true(approve_res.status_code == 200, f"Admin approved coordinator application: {approve_res.status_code}")
    assert_true(approve_res.json()["status"] == "APPROVED", "Status updated to APPROVED")

    # Candidate logs in again - role must now be EVENT_COORDINATOR!
    coord_login_post = requests.post(f"{BASE_URL}/auth/login", json={
        "email": coord_email,
        "password": "password123"
    })
    assert_true(coord_login_post.json()["user"]["role"] == "EVENT_COORDINATOR", f"User promoted to EVENT_COORDINATOR: {coord_login_post.json()['user']['role']}")

    # 3. Judge Cryptographic Invitation Workflow
    print_test("3. Judge Cryptographic Invitation Workflow")
    judge_email = f"judge_{rand_id}@expert-jury.org"

    # Non-admin cannot issue invitations
    unauth_invite = requests.post(
        f"{BASE_URL}/admin/invitations",
        headers={"Authorization": f"Bearer {tamper_token}"},
        json={
            "email": judge_email,
            "role": "JUDGE",
            "organization": "Hackathon Jury Inc",
            "specialization": "Distributed Systems",
            "expires_in_days": 7
        }
    )
    assert_true(unauth_invite.status_code == 403, f"Non-admin rejected from issuing invitations (403): {unauth_invite.status_code}")

    # Admin creates valid Judge invitation
    admin_invite = requests.post(
        f"{BASE_URL}/admin/invitations",
        headers=admin_headers,
        json={
            "email": judge_email,
            "role": "JUDGE",
            "organization": "National Tech Council",
            "specialization": "Web3 & Cloud Architecture",
            "expires_in_days": 5
        }
    )
    assert_true(admin_invite.status_code == 201, f"Admin successfully issued invitation: {admin_invite.status_code}")
    inv_data = admin_invite.json()
    raw_token = inv_data["raw_token"]
    assert_true(bool(raw_token), "Single-use raw cryptographic token returned to admin")
    assert_true(inv_data["status"] == "PENDING", "Invitation starts in PENDING status")

    # Public verification of token
    verify_res = requests.get(f"{BASE_URL}/invitations/verify", params={"token": raw_token})
    assert_true(verify_res.status_code == 200, "Token verification endpoint succeeded")
    v_data = verify_res.json()
    assert_true(v_data["valid"] is True, "Token confirmed valid")
    assert_true(v_data["email"] == judge_email, f"Token bound to recipient email: {v_data['email']}")
    assert_true(v_data["role"] == "JUDGE", f"Token role confirmed as JUDGE: {v_data['role']}")

    # Attack: An unauthorized user tries to accept the invitation with their own email
    hijack_res = requests.post(f"{BASE_URL}/invitations/accept", json={
        "token": raw_token,
        "email": "hijacker@evil.com",  # ATTACK: Email mismatch
        "password": "password123",
        "full_name": "Token Hijacker"
    })
    assert_true(hijack_res.status_code in [400, 403], f"Token email tampering rejected ({hijack_res.status_code}): {hijack_res.text}")

    # Legitimate acceptance
    accept_res = requests.post(f"{BASE_URL}/invitations/accept", json={
        "token": raw_token,
        "email": judge_email,
        "password": "password123",
        "full_name": "Dr. Verified Judge",
        "phone": "+91 8888777766",
        "bio": "Distinguished Professor and Hackathon Judge"
    })
    assert_true(accept_res.status_code == 200, f"Legitimate judge accepted invitation: {accept_res.status_code}")
    accept_data = accept_res.json()
    assert_true(accept_data["user"]["role"] == "JUDGE", f"Session returned with JUDGE role: {accept_data['user']['role']}")
    judge_jwt = accept_data["access_token"]

    # Attack: Reusing the same token (Single-use replay attack)
    replay_res = requests.post(f"{BASE_URL}/invitations/accept", json={
        "token": raw_token,
        "email": judge_email,
        "password": "password123",
        "full_name": "Replay Attacker"
    })
    assert_true(replay_res.status_code == 400, f"Replay attack prevented, token is single-use ({replay_res.status_code}): {replay_res.text}")

    # 4. Sponsor Application Workflow
    print_test("4. Corporate Sponsor Proposal & Approval Workflow")
    spon_email = f"sponsor_{rand_id}@brand.com"
    spon_payload = {
        "company_name": f"TechCorp Global {rand_id}",
        "industry": "Artificial Intelligence",
        "contact_name": "Sarah Connor",
        "email": spon_email,
        "phone": "+1 555 123 4567",
        "website": "https://techcorp.example.com",
        "proposed_tier": "Platinum Partner",
        "proposal_message": "Excited to sponsor the flagship AI hackathon."
    }

    spon_res = requests.post(f"{BASE_URL}/auth/apply/sponsor", json=spon_payload)
    assert_true(spon_res.status_code in [200, 201], f"Sponsor proposal submitted: {spon_res.status_code}")
    spon_id = spon_res.json()["id"]

    # Admin reviews and approves sponsor proposal
    spon_appr = requests.post(
        f"{BASE_URL}/admin/applications/sponsors/{spon_id}/approve",
        headers=admin_headers,
        json={"admin_notes": "Platinum tier contract finalized."}
    )
    assert_true(spon_appr.status_code == 200, f"Admin approved sponsor proposal: {spon_appr.status_code}")
    assert_true(spon_appr.json()["status"] == "APPROVED", "Sponsor status is APPROVED")

    # 5. Unauthenticated Access Protection
    print_test("5. Authorization Boundary Checks")
    unauth_req = requests.get(f"{BASE_URL}/admin/applications/coordinators")
    assert_true(unauth_req.status_code == 401, f"Unauthenticated request returns 401: {unauth_req.status_code}")

    forbidden_req = requests.get(
        f"{BASE_URL}/admin/applications/coordinators",
        headers={"Authorization": f"Bearer {tamper_token}"}
    )
    assert_true(forbidden_req.status_code == 403, f"Unauthorized role returns 403: {forbidden_req.status_code}")

    print("\n=======================================================")
    print("🎉 ALL SECURITY WORKFLOW TESTS PASSED PERFECTLY!")
    print("=======================================================\n")

if __name__ == "__main__":
    main()
