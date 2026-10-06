# CAMPUSFEST — Production-Ready College Fest Management System

A full-stack, enterprise-grade College Fest Management Platform engineered with **FastAPI**, **SQLAlchemy 2.0**, **Alembic**, **PostgreSQL/MySQL/SQLite**, and **React (Vite + Tailwind CSS v4)**.

---

## 🌟 Architecture Overview

```
                                  +------------------------------------+
                                  |         React 19 Frontend          |
                                  |  (Vite + Tailwind CSS v4 + Lucide) |
                                  +------------------------------------+
                                                    |
                                      HTTPS REST APIs / Multipart Media
                                                    |
                                                    v
                                  +------------------------------------+
                                  |          FastAPI Backend           |
                                  |   (JWT RBAC + PyJWT + Passlib/BC)  |
                                  +------------------------------------+
                                       /            |            \
                                      /             |             \
                                     v              v              v
                  +---------------------+   +---------------+   +-------------------+
                  |   SQLAlchemy 2.0    |   |  Media Storage|   | ReportLab Vector  |
                  |  Alembic Migrations |   |  (Pillow Mime |   |   PDF Engine &    |
                  | (Production RDBMS)  |   |  & Traversal) |   |  QRCode Generator |
                  +---------------------+   +---------------+   +-------------------+
```

---

## 🚀 Key Modules & Capabilities

1. **Authentication & Strict Role-Based Access Control (RBAC):**
   - Pure database-driven role resolution (`STUDENT`, `EVENT_COORDINATOR`, `JUDGE`, `ADMIN`, `SPONSOR`, `GUEST`).
   - Secure bcrypt password hashing and PyJWT token generation.
   - Zero hardcoded roles, no role-selector dropdown on login.
   - Real profiles for Students, Coordinators, Judges, and Sponsors.

2. **Mandatory Event Visual & Media Management:**
   - Real event-specific cover and banner image upload (`POST /api/events/{id}/media`).
   - Drag-and-drop, image preview, replace, and remove capabilities.
   - Server-side MIME validation, Pillow image verification, dimension extraction, and directory traversal protection.
   - Seamless presentation across public catalog cards and hero detail pages.

3. **Solo & Team Registration Engine:**
   - Registration flow supporting solo and squad entries with customizable team capacity limits.
   - Unique invite codes for squad formation (`TM-XXXXXX`).
   - Registration deadline enforcement with timezone-aware datetime validation.

4. **Payments, Orders & Automated Tax Invoices:**
   - Payment order creation, simulated transaction verification, and automatic `Invoice` generation with GST breakdown.
   - Itemized fiscal ledgers and printable receipts.

5. **Tamper-Resistant QR Ticket Passes & Gate Scanner:**
   - Cryptographically hashed ticket signatures.
   - Embedded high-res base64 PNG QR code tickets with one-click download and print.
   - Live camera scanner (`html5-qrcode`) and manual code check-in.
   - **Duplicate Entry Prevention**: Atomic check-in checks return `409 Conflict` on duplicate scan attempts.

6. **Judging Panels, Weighted Rubrics & Auto-Leaderboards:**
   - Coordinator assignment of certified judges to specific events.
   - Dynamic evaluation rubrics with custom weightage factors and point ceilings.
   - Real-time aggregated leaderboard calculations.
   - Final results publishing triggering automated certificate generation.

7. **Cryptographic Certificate Generation & Public Verification:**
   - Vector landscape PDF certificates dynamically generated using ReportLab with official styling.
   - Public certificate verification page (`/verify/:hash`) with SHA-256 integrity checks.

8. **Sponsor Tiers, Promos & Real-Time Analytics:**
   - Tier packages (`TITLE`, `PLATINUM`, `GOLD`, etc.).
   - Banner slot deployments with click-through rate (CTR) and impression tracking.
   - Aggregate operational metrics and audit logging across all entities.

---

## 🛠️ Project Structure

```
event/
├── backend/
│   ├── alembic/                      # Alembic migration configurations & versions
│   │   ├── versions/
│   │   │   └── 50f353fc99de_initial_schema.py
│   │   └── env.py
│   ├── app/
│   │   ├── api/v1/                   # FastAPI REST API endpoints
│   │   │   ├── admin.py
│   │   │   ├── announcements.py
│   │   │   ├── attendance.py
│   │   │   ├── auth.py
│   │   │   ├── certificates.py
│   │   │   ├── events.py             # Event CRUD + Media Upload
│   │   │   ├── judges.py
│   │   │   ├── notifications.py
│   │   │   ├── payments.py
│   │   │   ├── public.py
│   │   │   ├── registrations.py
│   │   │   ├── results.py
│   │   │   ├── scores.py
│   │   │   ├── sponsors.py
│   │   │   ├── teams.py
│   │   │   └── users.py
│   │   ├── core/                     # Config, security, dependencies
│   │   │   ├── config.py
│   │   │   ├── dependencies.py
│   │   │   └── security.py
│   │   ├── db/                       # Base declarative & engine session
│   │   ├── models/                   # 29 SQLAlchemy ORM database models
│   │   ├── schemas/                  # Pydantic v2 validation schemas
│   │   ├── services/                 # Business logic & services
│   │   │   ├── analytics_service.py
│   │   │   ├── attendance_service.py
│   │   │   ├── audit_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── certificate_service.py
│   │   │   ├── judging_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── payment_service.py
│   │   │   ├── qr_service.py
│   │   │   └── storage_service.py
│   │   └── main.py                   # FastAPI entrypoint, CORS, static mounts
│   ├── tests/                        # Comprehensive Pytest test suite
│   ├── uploads/                      # Uploaded event media storage
│   ├── .env.example
│   ├── alembic.ini
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── api/                      # Axios API clients
    │   ├── auth/                     # AuthContext, ProtectedRoute, RoleRoute
    │   ├── components/               # StatusBadge, EventCard, ImageUploadSection,
    │   │                             # EventPreviewModal, QRPassModal, QRScannerModal,
    │   │                             # PaymentModal, NotificationCenter, StatCard, EmptyState
    │   ├── layouts/                  # Public, Dashboard, Student, Coordinator, Judge, Admin, Sponsor
    │   ├── pages/
    │   │   ├── auth/                 # Login, Register, 403 Forbidden, 404 NotFound
    │   │   ├── public/               # Home, Events, EventDetail, Schedule, Venues,
    │   │   │                         # Announcements, PublicResults, CertificateVerify
    │   │   ├── student/              # Dashboard, Registrations, Teams, Payments, Passes, Certificates, Profile
    │   │   ├── coordinator/          # Dashboard, Events (Builder), Participants, Judges, Attendance, Results, Analytics
    │   │   ├── judge/                # Dashboard, Events, Scoring (Rubrics), Rankings
    │   │   ├── admin/                # Dashboard, Users, Events, Sponsors, Revenue, AuditLogs
    │   │   └── sponsor/              # Dashboard, Plans, Promotions, Analytics
    │   ├── App.jsx                   # Central RBAC Router
    │   ├── main.jsx
    │   └── index.css                 # Tailwind CSS v4 styling
    ├── package.json
    └── vite.config.js
```

---

## ⚡ Getting Started

### Prerequisites
- **Python 3.10+** (Python 3.13 supported)
- **Node.js 18+** & npm
- PostgreSQL, MySQL, or SQLite

---

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Set your actual database credentials in `.env`:
   ```ini
   DATABASE_URL=postgresql://user:password@localhost:5432/fest_db
   JWT_SECRET_KEY=your_secure_random_secret_key_here
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=120
   CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]
   EVENT_MEDIA_STORAGE=local
   EVENT_MEDIA_PATH=uploads/events
   ```

5. **Apply Database Migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Run Backend Tests:**
   ```bash
   python -m pytest -v
   ```

7. **Start the FastAPI Server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Interactive Swagger API Documentation will be available at `http://localhost:8000/docs`.

---

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd ../frontend
   ```

2. **Install frontend dependencies:**
   ```bash
   npm install
   ```

3. **Configure Environment:**
   Ensure `frontend/.env` is present:
   ```ini
   VITE_API_BASE_URL=/api
   ```

4. **Build for Production:**
   ```bash
   npm run build
   ```

5. **Start Development Server:**
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

---

## 🔒 Security & RBAC Enforcement

- **Role Authorization Dependency:** Every administrative and operational endpoint is guarded by `require_role(allowed_roles)`. If an unauthorized role attempts to access an endpoint (e.g. a Student calling Admin endpoints), a `403 Forbidden` response is returned.
- **Media Upload Traversal Protection:** All uploaded image filenames are replaced with cryptographic UUIDs and stored with strict path resolution to prevent directory traversal attacks.
- **Duplicate Ticket Prevention:** Once an attendee's QR ticket pass is scanned at the entrance gate, consecutive attempts are immediately rejected with `409 Conflict (DUPLICATE_ENTRY)`.
- **Audit Logging:** Every user role modification, event status update, ticket check-in, and scoring submission is recorded in the immutable `audit_logs` table with timestamp, IP address, and actor metadata.
