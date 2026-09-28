import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import check_db_connection, Base, engine
import app.models  # Ensures all models are registered

# Import all routers
from app.routers import (
    auth, events, student, teams, registrations,
    payments, passes, attendance, coordinator,
    judges, certificates, notifications, admin, sponsors, ai
)

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("festora")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing FESTORA Backend...")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "passes"), exist_ok=True)
    os.makedirs(settings.CERTIFICATES_DIR, exist_ok=True)

    db_ok = check_db_connection()
    if db_ok:
        logger.info("Successfully connected to MySQL database.")
    else:
        logger.warning("Could not establish initial database connection.")
    yield
    logger.info("Shutting down FESTORA Backend.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware for React frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for passes, QR images, certificates, and media
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CERTIFICATES_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint verifying API status.
    """
    return {
        "message": "FESTORA API is running",
        "version": settings.VERSION,
        "docs": "/docs",
        "status": "healthy"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint verifying database connectivity.
    """
    db_connected = check_db_connection()
    return {
        "status": "ok" if db_connected else "degraded",
        "database": "connected" if db_connected else "disconnected",
        "environment": "development" if settings.DEBUG else "production"
    }


# Include all routers prefixed by settings.API_V1_PREFIX (/api)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(events.router, prefix=settings.API_V1_PREFIX)
app.include_router(student.router, prefix=settings.API_V1_PREFIX)
app.include_router(teams.router, prefix=settings.API_V1_PREFIX)
app.include_router(registrations.router, prefix=settings.API_V1_PREFIX)
app.include_router(payments.router, prefix=settings.API_V1_PREFIX)
app.include_router(passes.router, prefix=settings.API_V1_PREFIX)
app.include_router(attendance.router, prefix=settings.API_V1_PREFIX)
app.include_router(coordinator.router, prefix=settings.API_V1_PREFIX)
app.include_router(judges.router, prefix=settings.API_V1_PREFIX)
app.include_router(certificates.router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(sponsors.router, prefix=settings.API_V1_PREFIX)
app.include_router(ai.router, prefix=settings.API_V1_PREFIX)
