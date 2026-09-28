# FESTORA API — College Fest Management Platform Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=flat&logo=mysql)](https://mysql.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=flat)](https://sqlalchemy.org)
[![Tests](https://img.shields.io/badge/Tests-12%20Passed-brightgreen)](https://pytest.org)

The robust REST API backend powering **FESTORA**, designed to match the React frontend screens and user journeys. Built with a clean layered architecture: **Router → Schema → Service → Model → MySQL**.

---

## 🏛️ System Architecture

```
                    REACT FRONTEND
                     (Your Friend)
                          │
                          │ REST API / JSON
                          ▼
                 ┌──────────────────┐
                 │     FASTAPI      │
                 │   (festora_api)  │
                 ├──────────────────┤
                 │ Auth & RBAC      │
                 │ Users            │
                 │ Events           │
                 │ Registrations    │
                 │ Teams            │
                 │ Payments         │
                 │ QR Pass          │
                 │ Attendance       │
                 │ Schedule         │
                 │ Judges           │
                 │ Scoring          │
                 │ Leaderboard      │
                 │ Certificates     │
                 │ Notifications    │
                 │ Sponsors         │
                 │ Analytics        │
                 │ FEST AI          │
                 └────────┬─────────┘
                          │
                          ▼
                    ┌───────────┐
                    │   MySQL   │
                    │festora_db │
                    └───────────┘
```

---

## 🗺️ Frontend Screen to FastAPI Route Mapping

| Friend's React Feature | Your FastAPI Endpoint | Method | Role Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Landing page statistics** | `/api/public/stats` | `GET` | Public | Real-time counts of events, colleges, participants, prize pool |
| **Event discovery** | `/api/events` | `GET` | Public | Multi-filter discovery: category, price, date, team size, search |
| **Search events** | `/api/events/search` | `GET` | Public | Keyword search across event title, description, and short blurbs |
| **Event details** | `/api/events/{id}` | `GET` | Public | Full event view: about, rules, rounds, judging criteria, prizes, venue, faqs |
| **Schedule / Timeline** | `/api/schedule` | `GET` | Public | Chronological fest schedule grouped by day & venue |
| **Registration flow** | `/api/registrations` | `POST` | Student | Deadline checks, capacity validation, duplicate prevention, team check |
| **Student dashboard** | `/api/student/dashboard` | `GET` | Student | User greeting, registered stats, next event card, AI match recommendations |
| **My events** | `/api/student/events` | `GET` | Student | All events registered by student with pass status |
| **My team** | `/api/teams/my` | `GET` | Student | Active team memberships and created squads |
| **Create team** | `/api/teams` | `POST` | Student | Form a new competition team and generate unique join code |
| **Join team** | `/api/teams/join` | `POST` | Student | Join an existing team using invite code |
| **Team invitations** | `/api/teams/{id}/invite` | `POST` | Student | Invite fellow students by email |
| **Payment processing** | `/api/payments` | `POST` | Student | Payment confirmation, auto invoice generation, QR pass activation |
| **My Fest Pass** | `/api/student/pass/{id}` | `GET` | Student | Rendered digital pass with participant name, venue, time, QR token |
| **QR verification** | `/api/attendance/scan` | `POST` | Coordinator | Validates pass QR token, detects duplicate attendance, logs live check-in |
| **Coordinator dashboard** | `/api/coordinator/dashboard` | `GET` | Coordinator | Assigned events, registered totals, checked-in numbers, attendance rate |
| **Live attendance list** | `/api/coordinator/attendance` | `GET` | Coordinator | Real-time participant check-in log with exact timestamps |
| **Judge dashboard** | `/api/judge/dashboard` | `GET` | Judge | Assigned competitions and evaluation progress |
| **Judge scoring** | `/api/judge/evaluations` | `POST` | Judge | Innovation + Technical + Presentation scoring with auto total computation |
| **Leaderboard** | `/api/events/{id}/leaderboard` | `GET` | Public | Live dynamic rankings dynamically computed from judge evaluations |
| **Certificates** | `/api/certificates` | `GET` | Student | List of earned verified certificates |
| **Certificate verification** | `/api/certificates/verify/{id}` | `GET` | Public | Public certificate authentication page |
| **Download PDF certificate** | `/api/certificates/{id}/download`| `GET` | Public | On-the-fly generated high-res PDF certificate |
| **Admin dashboard** | `/api/admin/dashboard` | `GET` | Admin | Users, active events, gross revenue, overall fest attendance % |
| **Fest analytics** | `/api/admin/analytics` | `GET` | Admin | 7-day registration curve, category revenue, top colleges |
| **User directory** | `/api/admin/users` | `GET` | Admin | Role-protected user directory (`Admin access required`) |
| **Sponsors showcase** | `/api/sponsors` | `GET` | Public | Official partners showcase with tiers and links |
| **Sponsorship plans** | `/api/sponsors/plans` | `GET` | Public | Available sponsorship tiers and perks |
| **Notifications** | `/api/notifications` | `GET` | Authenticated | Live reminders, schedule changes, and pass confirmations |
| **FEST AI Assistant** | `/api/ai/chat` | `POST` | Public/User | Intent-driven query engine querying live DB, returns structured actions |

---

## 🔐 Role-Based Access Control (RBAC)

The backend implements strict role-based access control. Every user token contains cryptographically verified role claims (`STUDENT`, `COORDINATOR`, `JUDGE`, `ADMIN`, `SPONSOR`).

```
student ───► /api/student/dashboard  ──►  200 OK (Joyal's personalized data)
student ───► /api/admin/users        ──►  403 Forbidden: {"detail": "Admin access required"}
admin   ───► /api/admin/users        ──►  200 OK (Full user directory)
```

---

## 🤖 FEST AI — Deep Database Integration & Structured Actions

Unlike an isolated chat widget, **FEST AI** interprets student natural language intent, executes targeted queries against the live MySQL tables (Events, Schedules, Registrations, Venues), and returns actionable UI responses:

**User Query**:
> *"What technical events are happening?"*

**Response Payload**:
```json
{
  "message": "I found 3 technical events happening at FESTORA. Here are the top picks:",
  "type": "event_list",
  "data": [
    {
      "id": 14,
      "name": "Code Sprint",
      "time": "10:00 AM",
      "venue": "Computer Lab 2",
      "registration_fee": 150.0
    }
  ],
  "actions": [
    {
      "type": "VIEW_EVENT",
      "event_id": 14,
      "label": "View Code Sprint"
    }
  ],
  "session_id": "sess_89f1ab"
}
```

The React frontend simply parses `actions` to render interactive buttons like `[ View Code Sprint → ]`.

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- MySQL 8.0 running on `localhost:3306`

### 2. Virtual Environment & Dependencies
```powershell
cd festora_backend
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

### 3. Environment Configuration (`.env`)
Verify `.env` has your MySQL credentials:
```env
DATABASE_URL=mysql+pymysql://root:root%40123@localhost:3306/festora_db
SECRET_KEY=festora_super_secret_jwt_key_development_2026_festora_api_secure
ALGORITHM=HS256
```

### 4. Database Schema Migrations & Seeding
```powershell
# Run migrations (already stamped head)
.\venv\Scripts\alembic upgrade head

# Seed realistic demo data matching the specification
.\venv\Scripts\python seed_data.py
```

### 5. Start FastAPI Server
```powershell
.\venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **API Root**: `http://127.0.0.1:8000/`
- **Interactive Swagger Documentation**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`

---

## 🧪 Automated Test Suite

Run the full pytest integration suite:
```powershell
.\venv\Scripts\pytest -v
```

All 12 critical user flows pass:
```
tests/test_api.py::test_root_endpoint PASSED
tests/test_api.py::test_public_stats PASSED
tests/test_api.py::test_event_discovery_and_filtering PASSED
tests/test_api.py::test_event_details_endpoint PASSED
tests/test_api.py::test_auth_login_and_role_tokens PASSED
tests/test_api.py::test_role_based_access_control PASSED
tests/test_api.py::test_student_dashboard PASSED
tests/test_api.py::test_fest_pass_endpoint PASSED
tests/test_api.py::test_coordinator_qr_scan PASSED
tests/test_api.py::test_leaderboard_automatic_rankings PASSED
tests/test_api.py::test_fest_ai_structured_actions PASSED
tests/test_api.py::test_certificate_verification PASSED
```

---

## 🎤 Presentation Story for the Evaluation Panel

When asked by the panel:

**"What did you build for the backend?"**
> *"I architected and developed the complete REST API for FESTORA using FastAPI, SQLAlchemy 2.0, and MySQL. Rather than building generic CRUD endpoints, I designed the API contract directly around the React frontend user journeys. The backend implements role-based access control (RBAC) across Students, Coordinators, Judges, Admins, and Sponsors. It handles end-to-end event discovery, multi-participant registrations, payment validation with automatic invoice generation, cryptographic QR fest passes, real-time attendance check-in, judging with dynamic multi-evaluator leaderboard computation, and automated PDF certificate generation."*

**"How does the AI feature work?"**
> *"FEST AI is deeply integrated into the backend application layer rather than acting as a standalone prompt bot. When a user asks questions about events, schedules, or their passes, the FastAPI service extracts intent, performs targeted relational queries on the MySQL database, and returns structured action cards with interactive frontend triggers (like VIEW_EVENT or REGISTER_NOW) so the user can act directly within the UI."*
