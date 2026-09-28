from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.student import StudentDashboardOut, RecommendationOut
from app.schemas.registration import RegistrationOut
from app.schemas.pass_attendance import FestPassOut
from app.services.student_service import StudentService
from app.services.registration_service import RegistrationService
from app.services.attendance_service import AttendanceService

router = APIRouter(tags=["Student Platform"])


@router.get("/student/dashboard", response_model=StudentDashboardOut)
def get_student_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Personalized student dashboard endpoint returning registration statistics,
    next upcoming event card, and tailored recommendations.
    """
    return StudentService.get_dashboard(db, current_user)


@router.get("/student/events", response_model=List[RegistrationOut])
def get_my_registered_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List of all events registered by the student."""
    return RegistrationService.get_my_registrations(db, current_user)


@router.get("/recommendations", response_model=List[RecommendationOut])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Personalized event recommendations based on user interests."""
    dashboard = StudentService.get_dashboard(db, current_user)
    return dashboard.recommendations


@router.get("/student/pass/{registration_id}", response_model=FestPassOut)
def get_student_fest_pass(
    registration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve verified Fest Pass with QR code for an event registration."""
    return AttendanceService.get_pass_by_registration(db, registration_id, current_user)
