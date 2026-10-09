import sys
import requests
import uuid

BASE_URL = "http://127.0.0.1:8000/api"

def print_test(name):
    print(f"\n=======================================================")
    print(f"RUNNING TEST: {name}")
    print(f"=======================================================")

def assert_true(condition, msg):
    if not condition:
        print(f"FAILED: {msg}")
        sys.exit(1)
    else:
        print(f"PASSED: {msg}")

def main():
    print("Beginning EventX Judge Registration & Sponsor Removal Verification...")

    # 0. Admin Login
    print_test("0. Admin Authentication")
    admin_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@college.edu",
        "password": "password123"
    })
    assert_true(admin_login.status_code == 200, "Admin credentials verified")
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    assert_true(admin_login.json()["user"]["role"] == "ADMIN", "Admin role confirmed")

    # 1. Judge Application (Same as Event Coordinator)
    print_test("1. Public Judge Candidacy Application (/auth/apply/judge)")
    rand_id = uuid.uuid4().hex[:6]
    judge_email = f"judge_candidate_{rand_id}@jury.org"
    judge_payload = {
        "full_name": f"Dr. Elena Rostova {rand_id}",
        "email": judge_email,
        "password": "password123",
        "phone": "+91 9123456789",
        "organization": "National Institute of AI & Robotics",
        "specialization": "Artificial Intelligence & Distributed Algorithms",
        "experience": "Chaired 4 national hackathon juries; IEEE Senior Member.",
        "bio": "Distinguished researcher and jury veteran."
    }

    apply_res = requests.post(f"{BASE_URL}/auth/apply/judge", json=judge_payload)
    assert_true(apply_res.status_code in [200, 201], f"Judge application submitted: {apply_res.status_code}")
    app_data = apply_res.json()
    app_id = app_data["id"]
    assert_true(app_data["status"] == "PENDING", f"Application stored with PENDING status: {app_data['status']}")
    assert_true(app_data["organization"] == judge_payload["organization"], "Organization stored correctly")
    assert_true(app_data["specialization"] == judge_payload["specialization"], "Specialization stored correctly")

    # Candidate logs in before approval - role must be strictly STUDENT
    initial_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": judge_email,
        "password": "password123"
    })
    assert_true(initial_login.status_code == 200, "Candidate can authenticate")
    assert_true(initial_login.json()["user"]["role"] == "STUDENT", f"Unapproved judge has unprivileged STUDENT role: {initial_login.json()['user']['role']}")
    candidate_token = initial_login.json()["access_token"]

    # Candidate checks their status
    status_res = requests.get(f"{BASE_URL}/auth/application/status", params={"email": judge_email})
    assert_true(status_res.status_code == 200, "Candidate can query their application status")
    st_data = status_res.json()
    assert_true("judge_application" in st_data, "judge_application returned in status response")
    assert_true(st_data["judge_application"]["status"] == "PENDING", "Status confirms PENDING")
    assert_true("sponsor_application" not in st_data, "sponsor_application is not present (sponsor module removed)")

    # 2. Candidate Cannot Self-Approve
    print_test("2. Self-Approval Privilege Escalation Prevention")
    self_approve = requests.post(
        f"{BASE_URL}/admin/applications/judges/{app_id}/approve",
        headers={"Authorization": f"Bearer {candidate_token}"},
        json={"admin_notes": "Attempting self elevation"}
    )
    assert_true(self_approve.status_code == 403, f"Unauthorized candidate denied approval action (403 Forbidden): {self_approve.status_code}")

    # 3. Admin Reviews & Approves Judge Application
    print_test("3. Admin Approval Workflow (/admin/applications/judges/{id}/approve)")
    list_apps = requests.get(f"{BASE_URL}/admin/applications/judges", headers=admin_headers)
    assert_true(list_apps.status_code == 200, "Admin can list judge applications")
    found = any(a["id"] == app_id for a in list_apps.json())
    assert_true(found, "Newly submitted judge application visible in Admin console")

    approve_res = requests.post(
        f"{BASE_URL}/admin/applications/judges/{app_id}/approve",
        headers=admin_headers,
        json={"admin_notes": "Credentials verified with IEEE panel."}
    )
    assert_true(approve_res.status_code == 200, f"Admin approved judge application: {approve_res.status_code}")
    assert_true(approve_res.json()["status"] == "APPROVED", "Status updated to APPROVED")

    # Candidate logs in again - role must now be promoted to JUDGE!
    post_approval_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": judge_email,
        "password": "password123"
    })
    assert_true(post_approval_login.status_code == 200, "Candidate can authenticate post-approval")
    assert_true(post_approval_login.json()["user"]["role"] == "JUDGE", f"Candidate successfully promoted to JUDGE: {post_approval_login.json()['user']['role']}")

    # 4. Admin Rejection Workflow
    print_test("4. Judge Rejection Workflow")
    reject_email = f"judge_reject_{rand_id}@unqualified.org"
    reject_apply = requests.post(f"{BASE_URL}/auth/apply/judge", json={
        "full_name": "Unqualified Applicant",
        "email": reject_email,
        "password": "password123",
        "organization": "Unknown Entity",
        "specialization": "General"
    })
    assert_true(reject_apply.status_code in [200, 201], "Second candidate application submitted")
    reject_id = reject_apply.json()["id"]

    reject_res = requests.post(
        f"{BASE_URL}/admin/applications/judges/{reject_id}/reject",
        headers=admin_headers,
        json={"admin_notes": "Does not meet judging seniority criteria."}
    )
    assert_true(reject_res.status_code == 200, "Admin rejected application")
    assert_true(reject_res.json()["status"] == "REJECTED", "Status updated to REJECTED")

    reject_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": reject_email,
        "password": "password123"
    })
    assert_true(reject_login.json()["user"]["role"] == "STUDENT", "Rejected applicant remains unprivileged STUDENT")

    # 5. Verify Complete Elimination of Sponsor Module
    print_test("5. Sponsor Module Elimination Verification")
    spon_apply = requests.post(f"{BASE_URL}/auth/apply/sponsor", json={
        "company_name": "Test Company",
        "industry": "Tech",
        "contact_name": "Test",
        "email": "test@sponsor.com"
    })
    assert_true(spon_apply.status_code == 404, f"/auth/apply/sponsor is deactivated (404 Not Found): {spon_apply.status_code}")

    spon_admin = requests.get(f"{BASE_URL}/admin/applications/sponsors", headers=admin_headers)
    assert_true(spon_admin.status_code == 404, f"/admin/applications/sponsors is deactivated (404 Not Found): {spon_admin.status_code}")

    spon_plans = requests.get(f"{BASE_URL}/sponsors/plans")
    assert_true(spon_plans.status_code == 404, f"/sponsors/plans is deactivated (404 Not Found): {spon_plans.status_code}")

    print("\n=======================================================")
    print("ALL TESTS PASSED: Judge registration works identically to coordinator & Sponsor module is completely removed!")
    print("=======================================================\n")

if __name__ == "__main__":
    main()
