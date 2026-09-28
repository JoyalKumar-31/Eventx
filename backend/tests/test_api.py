"""
Comprehensive API integration tests for FESTORA Backend
Tests each user journey matching the React frontend specifications.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify root endpoint and API running status."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["message"] == "FESTORA API is running"
    assert data["status"] == "healthy"


def test_public_stats():
    """Verify landing page statistics."""
    res = client.get("/api/public/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_events"] >= 4
    assert data["total_categories"] >= 5


def test_event_discovery_and_filtering():
    """Verify event filtering by category and search."""
    # List all events
    res = client.get("/api/events")
    assert res.status_code == 200
    events = res.json()
    assert len(events) >= 4

    # Filter by category
    res_tech = client.get("/api/events?category=technical")
    assert res_tech.status_code == 200
    tech_events = res_tech.json()
    assert all(e["category"]["name"] == "Technical" for e in tech_events)

    # Search by keyword
    res_search = client.get("/api/events/search?q=code")
    assert res_search.status_code == 200
    assert any("Code" in e["name"] for e in res_search.json())


def test_event_details_endpoint():
    """Verify detailed event endpoint returning rules, rounds, prizes, venue and faqs."""
    res = client.get("/api/events/14")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 14
    assert data["name"] == "Code Sprint"
    assert data["venue"]["name"] == "Computer Lab 2"
    assert len(data["rules"]) > 0
    assert len(data["rounds"]) > 0
    assert len(data["prizes"]) > 0
    assert len(data["faqs"]) > 0


def test_auth_login_and_role_tokens():
    """Verify JWT authentication for Student, Coordinator, Judge, and Admin."""
    # Student Joyal login
    res_student = client.post("/api/auth/login", json={
        "email": "joyal@festora.com",
        "password": "password123"
    })
    assert res_student.status_code == 200
    joyal_token = res_student.json()["access_token"]
    assert joyal_token is not None

    # Admin login
    res_admin = client.post("/api/auth/login", json={
        "email": "admin@festora.com",
        "password": "admin123"
    })
    assert res_admin.status_code == 200
    admin_token = res_admin.json()["access_token"]
    assert admin_token is not None


def test_role_based_access_control():
    """
    CRITICAL RBAC TEST:
    Student attempting to access /api/admin/users must receive:
    { "detail": "Admin access required" } with status 403 Forbidden.
    Admin accessing /api/admin/users must succeed with status 200 OK.
    """
    # 1. Login student
    res_student = client.post("/api/auth/login", json={
        "email": "joyal@festora.com",
        "password": "password123"
    })
    student_token = res_student.json()["access_token"]

    # Student requests admin endpoint -> MUST FAIL with 403
    res_forbidden = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert res_forbidden.status_code == 403
    assert res_forbidden.json()["detail"] == "Admin access required"

    # 2. Login admin
    res_admin = client.post("/api/auth/login", json={
        "email": "admin@festora.com",
        "password": "admin123"
    })
    admin_token = res_admin.json()["access_token"]

    # Admin requests admin endpoint -> MUST SUCCEED with 200
    res_allowed = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_allowed.status_code == 200
    assert len(res_allowed.json()) > 0


def test_student_dashboard():
    """Verify Student Dashboard API matching the friend's React screen."""
    res_login = client.post("/api/auth/login", json={
        "email": "joyal@festora.com",
        "password": "password123"
    })
    token = res_login.json()["access_token"]

    res_dash = client.get(
        "/api/student/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_dash.status_code == 200
    data = res_dash.json()

    assert data["user"]["name"] == "Joyal Kumar"
    assert data["statistics"]["registered"] >= 1
    assert data["statistics"]["certificates"] >= 1
    assert len(data["recommendations"]) > 0


def test_fest_pass_endpoint():
    """Verify Fest Pass retrieval with verified status and QR token."""
    res_login = client.post("/api/auth/login", json={
        "email": "joyal@festora.com",
        "password": "password123"
    })
    token = res_login.json()["access_token"]

    res_pass = client.get(
        "/api/student/pass/9281",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_pass.status_code == 200
    data = res_pass.json()
    assert data["participant"] == "Joyal Kumar"
    assert data["event"] == "Code Sprint"
    assert data["venue"] == "Computer Lab 2"
    assert "FEST-PASS" in data["qr_token"]


def test_coordinator_qr_scan():
    """Verify coordinator QR attendance scanning."""
    res_coord = client.post("/api/auth/login", json={
        "email": "sarah@festora.com",
        "password": "password123"
    })
    token = res_coord.json()["access_token"]

    # Scan Joyal's QR pass
    res_scan = client.post(
        "/api/attendance/scan",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "qr_token": "FEST-PASS-9281-JOYAL-VERIFIED",
            "event_id": 14
        }
    )
    assert res_scan.status_code == 200
    data = res_scan.json()
    assert data["success"] is True
    assert data["participant"] == "Joyal Kumar"
    assert data["event"] == "Code Sprint"


def test_leaderboard_automatic_rankings():
    """Verify live competition leaderboard dynamically calculated from judge scores."""
    res = client.get("/api/events/19/leaderboard")
    assert res.status_code == 200
    data = res.json()
    assert data["event_name"] == "ByteHack 2026"
    leaderboard = data["leaderboard"]
    assert len(leaderboard) >= 3

    # Rank 1: BYTEFORCE (94.2)
    assert leaderboard[0]["team_name"] == "BYTEFORCE"
    assert leaderboard[0]["rank"] == 1
    assert leaderboard[0]["score"] == 94.2

    # Rank 2: CODEX (91.8)
    assert leaderboard[1]["team_name"] == "CODEX"
    assert leaderboard[1]["rank"] == 2
    assert leaderboard[1]["score"] == 91.8

    # Rank 3: DEBUGGERS (89.7)
    assert leaderboard[2]["team_name"] == "DEBUGGERS"
    assert leaderboard[2]["rank"] == 3
    assert leaderboard[2]["score"] == 89.7


def test_fest_ai_structured_actions():
    """Verify FEST AI returns intelligent intent answers and actionable cards."""
    # 1. Technical events query
    res = client.post("/api/ai/chat", json={
        "message": "What technical events are happening?"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "event_list"
    assert len(data["data"]) > 0
    assert any(a["type"] == "VIEW_EVENT" for a in data["actions"])

    # 2. Schedule query
    res_sched = client.post("/api/ai/chat", json={
        "message": "Show me the festival schedule"
    })
    assert res_sched.status_code == 200
    data_sched = res_sched.json()
    assert data_sched["type"] == "schedule_list"
    assert any(a["type"] == "VIEW_SCHEDULE" for a in data_sched["actions"])


def test_certificate_verification():
    """Verify public certificate verification."""
    res = client.get("/api/certificates/verify/FEST-2026-CS-9281")
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert data["participant_name"] == "Joyal Kumar"
    assert data["event_name"] == "Code Sprint"


def test_fest_agents_query_network():
    """Verify teammate's multi-agent supervisor dispatching and execution."""
    # 1. Event agent route
    res_ev = client.post("/api/ai/agents/query", json={
        "question": "What are the rules and venue for Code Sprint?",
        "role": "student"
    })
    assert res_ev.status_code == 200
    data_ev = res_ev.json()
    assert data_ev["route_taken"] == "event_agent"
    assert "Computer Lab 2" in data_ev["response"]
    assert len(data_ev["trace"]) > 0

    # 2. Participant agent route
    res_part = client.post("/api/ai/agents/query", json={
        "question": "Check my registration status for REG-9281",
        "role": "student"
    })
    assert res_part.status_code == 200
    data_part = res_part.json()
    assert data_part["route_taken"] == "participant_agent"
    assert "REG-9281" in data_part["response"]

    # 3. Judging agent route
    res_judge = client.post("/api/ai/agents/query", json={
        "question": "Show live rankings for ByteHack 2026",
        "role": "judge"
    })
    assert res_judge.status_code == 200
    data_judge = res_judge.json()
    assert data_judge["route_taken"] == "judging_agent"
    assert "BYTEFORCE" in data_judge["response"]

    # 4. Sponsor & analytics agent route
    res_stat = client.post("/api/ai/agents/query", json={
        "question": "Give me the real-time fest analytics and revenue",
        "role": "admin"
    })
    assert res_stat.status_code == 200
    data_stat = res_stat.json()
    assert data_stat["route_taken"] == "sponsor_analytics_agent"
    assert "Revenue" in data_stat["response"]


def test_fest_agents_info_directory():
    """Verify GET /api/ai/agents/info returns all 7 specialized agents."""
    res = client.get("/api/ai/agents/info")
    assert res.status_code == 200
    agents = res.json()
    assert len(agents) == 7

    agent_ids = {a["agent_id"] for a in agents}
    expected_ids = {
        "supervisor",
        "event_agent",
        "participant_agent",
        "judging_agent",
        "result_cert_agent",
        "sponsor_analytics_agent",
        "faq_agent"
    }
    assert agent_ids == expected_ids

