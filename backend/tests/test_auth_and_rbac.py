import pytest
from app.models.enums import UserRole


def test_register_and_login_student(client):
    # 1. Register student
    reg_payload = {
        "email": "test_student@example.edu",
        "password": "Password123!",
        "full_name": "Alice Student",
        "role": "STUDENT",
        "student_profile": {
            "college_name": "MIT College",
            "student_id_number": "MIT-2024-001",
            "department": "Computer Science",
            "year_of_study": "3rd Year"
        }
    }
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "test_student@example.edu"
    assert data["role"] == "STUDENT"

    # 2. Duplicate registration fails with 409
    res_dup = client.post("/api/auth/register", json=reg_payload)
    assert res_dup.status_code == 409

    # 3. Invalid login fails with 401
    res_bad = client.post("/api/auth/login", json={"email": "test_student@example.edu", "password": "WrongPassword"})
    assert res_bad.status_code == 401

    # 4. Valid login succeeds and returns access_token
    res_login = client.post("/api/auth/login", json={"email": "test_student@example.edu", "password": "Password123!"})
    assert res_login.status_code == 200
    login_data = res_login.json()
    assert "access_token" in login_data
    assert login_data["user"]["role"] == "STUDENT"

    # 5. Access /api/auth/me
    token = login_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    res_me = client.get("/api/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["full_name"] == "Alice Student"


def test_rbac_student_cannot_access_admin_endpoints(client):
    # Register student
    client.post("/api/auth/register", json={
        "email": "student_rbac@example.edu",
        "password": "Password123!",
        "full_name": "Bob Student",
        "role": "STUDENT"
    })
    token = client.post("/api/auth/login", json={
        "email": "student_rbac@example.edu",
        "password": "Password123!"
    }).json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Student calling admin metrics directly -> must return 403 Forbidden
    res_admin = client.get("/api/admin/metrics", headers=headers)
    assert res_admin.status_code == 403
    assert res_admin.json()["error_code"] == "FORBIDDEN"


def test_admin_access(client):
    # Register admin
    client.post("/api/auth/register", json={
        "email": "admin_sys@example.edu",
        "password": "AdminPassword123!",
        "full_name": "Chief Administrator",
        "role": "ADMIN"
    })
    token = client.post("/api/auth/login", json={
        "email": "admin_sys@example.edu",
        "password": "AdminPassword123!"
    }).json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Admin accessing admin metrics -> succeeds
    res_admin = client.get("/api/admin/metrics", headers=headers)
    assert res_admin.status_code == 200
    data = res_admin.json()
    assert "total_users" in data
    assert "total_events" in data
