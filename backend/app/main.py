import os
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1 import (
    auth,
    users,
    events,
    registrations,
    teams,
    payments,
    attendance,
    judges,
    scores,
    results,
    certificates,
    notifications,
    sponsors,
    announcements,
    admin,
    public
)

app = FastAPI(
    title="College Fest Management Application System",
    description="Production-Ready Full-Stack Enterprise Platform for College Fest Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {"name": "Authentication", "description": "User registration, login, and token management"},
        {"name": "Users", "description": "User profiles, roles, and administrative directory"},
        {"name": "Events", "description": "Event management, rules, rounds, venues, and media uploads"},
        {"name": "Registrations", "description": "Event enrollments and digital QR entry pass generation"},
        {"name": "Teams", "description": "Team creation, invitation codes, and member management"},
        {"name": "Payments", "description": "Payment orders, verification, and invoice tracking"},
        {"name": "Attendance", "description": "QR entry scanning, check-in validation, and duplicate prevention"},
        {"name": "Judging", "description": "Judge assignments, scoring criteria, and score submission"},
        {"name": "Results", "description": "Standings calculation and published results"},
        {"name": "Certificates", "description": "Dynamic PDF certificates and public verification"},
        {"name": "Notifications", "description": "In-app notifications and alerts"},
        {"name": "Sponsors", "description": "Sponsorship tiers, promotional slots, and engagement reach"},
        {"name": "Announcements", "description": "Fest announcements and targeted broadcasts"},
        {"name": "Admin", "description": "System analytics, audit trails, and revenue metrics"},
        {"name": "Public", "description": "Unauthenticated public schedules, stats, and venues"},
    ]
)

# CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploaded media
storage_root = os.path.abspath(settings.EVENT_MEDIA_PATH.split("/")[0] if "/" in settings.EVENT_MEDIA_PATH else "uploads")
os.makedirs(storage_root, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=storage_root), name="uploads")


# Centralized error response handler for consistent envelopes
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.detail),
            "error_code": "ERROR"
        }
    )


# Include API Routers under /api
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(registrations.router, prefix="/api")
app.include_router(teams.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(attendance.router, prefix="/api")
app.include_router(judges.router, prefix="/api")
app.include_router(scores.router, prefix="/api")
app.include_router(results.router, prefix="/api")
app.include_router(certificates.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(sponsors.router, prefix="/api")
app.include_router(announcements.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(public.router, prefix="/api")


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "College Fest Management Platform API",
        "environment": "production-ready"
    }
