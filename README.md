# Eventx — Modern College Fest Management Platform

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg)](https://www.mysql.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-FF6F00.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Eventx** (FESTORA) is a production-grade, end-to-end college fest management platform powering real-time event discovery, team registrations, automated UPI payments, cryptographically signed QR entry passes, judge scoring rubrics, live leaderboards, verifiable certificates, and a LangGraph multi-agent AI assistant network.

---

## 🏛️ System Architecture

```text
                           REACT FRONTEND
                            (Student / Coordinator / Judge / Admin UI)
                                 │
                                 │ REST API / JSON / JWT Bearer
                                 ▼
                 ┌────────────────────────────────┐
                 │       FASTAPI BACKEND          │
                 │   55 Endpoints (15 Routers)    │
                 ├────────────────────────────────┤
                 │   • Auth & RBAC (6 Roles)      │
                 │   • Event Engine & Venues      │
                 │   • Team & Registration Logic  │
                 │   • QR Passes & Attendance     │
                 │   • Judging & Leaderboards     │
                 │   • Sponsor Analytics          │
                 └───────────────┬────────────────┘
                                 │
                 ┌───────────────┴────────────────┐
                 │                                │
                 ▼                                ▼
  ┌─────────────────────────────┐  ┌─────────────────────────────┐
  │   LANGGRAPH AI NETWORK      │  │     MySQL 8.0 DATABASE      │
  │      (fest_agents/)         │  │     30 Relational Tables    │
  │ • Supervisor Agent          │  │ • users, roles, interests   │
  │ • Event Management Agent    │  │ • events, venues, rules     │
  │ • Participant & Team Agent  │  │ • teams, registrations      │
  │ • Judging & Evaluation Agent│  │ • payments, invoices        │
  │ • Result & Certificate Agent│  │ • passes, attendance        │
  │ • Sponsor & Analytics Agent │  │ • evaluations, results      │
  │ • FAQ & Helpdesk Agent      │  │ • certificates, sponsors    │
  └─────────────────────────────┘  └─────────────────────────────┘
```

---

## 🤖 The AI Multi-Agent Network (`fest_agents/`)

The multi-agent system uses **LangGraph** with dynamic supervisor intent classification, routing queries to specialized agents connected directly to the live MySQL database:

| Agent Name | Agent ID | Responsibilities | Live Tools Binding |
| :--- | :--- | :--- | :--- |
| **Supervisor Agent** | `supervisor` | Intent classification & dynamic routing based on user query and role. | Supervisor dispatch graph |
| **Event Management Agent** | `event_agent` | Event catalog lookup, venue navigation, rules, and clash detection. | `get_event_details`, `get_all_events`, `check_schedule_clash` |
| **Participant & Team Agent** | `participant_agent` | Validates team size, queries registration status, verifies QR gate passes. | `validate_team_size`, `check_registration_status`, `verify_qr_entry_pass` |
| **Judging & Evaluation Agent** | `judging_agent` | Scoring rubrics, weighted criteria, and live leaderboard rankings. | `get_evaluation_rubric`, `calculate_rankings`, `get_live_event_results` |
| **Result & Certificate Agent** | `result_cert_agent` | Generates official announcements and certificate verification text. | `generate_certificate_text`, `draft_announcement` |
| **Sponsor & Analytics Agent** | `sponsor_analytics_agent`| Computes live footfall, revenue, gate check-in rates, sponsor reports. | `get_fest_analytics`, `get_sponsor_reports` |
| **General FAQ & Helpdesk** | `faq_agent` | Campus directions, registration counters, UPI payment verification. | Helpdesk guidance & fallback |

---

## 📁 Repository Structure

```text
Eventx/
├── backend/                  # Complete FastAPI application
│   ├── app/
│   │   ├── core/             # Database config, JWT security, RBAC dependencies
│   │   ├── models/           # SQLAlchemy 2.0 ORM models (30 tables)
│   │   ├── routers/          # 15 FastAPI routers (55 endpoints)
│   │   ├── schemas/          # Pydantic v2 schemas
│   │   ├── services/         # Business logic & AI workflow integration
│   │   └── utils/            # QR code generation & PDF certificate builder
│   ├── fest_agents/          # Integrated AI multi-agent workflow
│   ├── migrations/           # Alembic database migrations
│   ├── tests/                # 14 integration tests (100% pass rate)
│   ├── alembic.ini           # Alembic migration configuration
│   ├── seed_data.py          # Realistic database seeder
│   ├── requirements.txt      # Backend dependencies
│   ├── .env.example          # Environment variables template
│   └── README.md             # Backend detailed documentation
├── fest_agents/              # Standalone AI agent module (LangGraph + Groq)
│   ├── tools/                # Domain-specific tool functions (MySQL-backed)
│   ├── graph.py              # StateGraph assembly & compilation
│   ├── nodes.py              # Agent node implementations
│   ├── routers.py            # Supervisor routing rules
│   ├── state.py              # AgentState TypedDict
│   ├── run_demo.py           # Multi-agent test suite & interactive CLI
│   └── README.md             # Agents module guide
├── .gitignore                # Comprehensive exclusions (.env, venv, caches)
└── README.md                 # Root documentation (this file)
```

---

## ⚡ Quickstart Guide

### 1. Prerequisites
- Python 3.11+ (tested on Python 3.13)
- MySQL Server 8.0 running locally on port 3306

### 2. Setup MySQL Database
```sql
CREATE DATABASE festora_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv

# On Windows:
.\venv\Scripts\activate

# On Linux/macOS:
source venv/bin/activate

# Install dependencies:
pip install -r requirements.txt
```

### 4. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Update your MySQL credentials in `.env`:
```env
DATABASE_URL=mysql+pymysql://root:your_mysql_password@localhost:3306/festora_db
DB_PASSWORD=your_mysql_password
SECRET_KEY=your_secure_secret_key_here
GROQ_API_KEY=your_groq_api_key_here  # Optional: For Llama 3.3 70B generation
```

### 5. Run Migrations & Seed Data
```bash
# Run database migrations
alembic upgrade head

# Populate sample fest data (users, events, teams, evaluations, passes)
python seed_data.py
```

### 6. Start FastAPI Server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open **`http://127.0.0.1:8000/docs`** for interactive Swagger documentation.

---

## 🧪 Testing the AI Agents

### Run Multi-Agent Automated Test Suite:
```bash
python fest_agents/run_demo.py
```

### Run Interactive Agent Chat CLI:
```bash
python fest_agents/run_demo.py --interactive
```

### Run Full Backend Integration Tests (14 Tests):
```bash
cd backend
pytest -v tests/test_api.py
```

---

## 📡 Core API Mappings

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Student/user registration |
| `POST` | `/api/auth/login` | JWT OAuth2 login with role-scoped tokens |
| `GET` | `/api/events` | Browse events with category/search filters |
| `POST` | `/api/registrations/individual` | Register for an individual competition |
| `POST` | `/api/teams/create` | Form a team with unique code |
| `POST` | `/api/payments/create-order` | Generate UPI / Gateway checkout order |
| `GET` | `/api/passes/my-pass` | Retrieve digital Fest Pass with QR code |
| `POST` | `/api/attendance/scan-qr` | Gate scanner entry validation |
| `POST` | `/api/judging/evaluate` | Judge score submission with rubrics |
| `GET` | `/api/events/{id}/leaderboard` | Live published rankings & scores |
| `GET` | `/api/certificates/verify/{id}`| Public certificate verification |
| `POST` | `/api/ai/chat` | Frontend conversational AI with Action Cards |
| `POST` | `/api/ai/agents/query` | Direct multi-agent network dispatching |
| `GET` | `/api/ai/agents/info` | Metadata directory for all 7 AI agents |

---

## 👥 Contributors

- **Joel Gera** — FastAPI Backend Architecture, MySQL Relational Database, Alembic Migrations, Live Tool Bindings
- **Dinesh** — Multi-Agent AI System Architecture, LangGraph Workflows, Prompt Engineering
- **Anil Kumar** — PDF Maker
