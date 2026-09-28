from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.user import User, RoleEnum
from app.schemas.pass_attendance import CoordinatorDashboardOut
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/coordinator", tags=["Coordinator Platform"])


@router.get("/dashboard", response_model=CoordinatorDashboardOut)
def get_coordinator_dashboard(
    current_user: User = Depends(require_role(RoleEnum.COORDINATOR, RoleEnum.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Live dashboard for event coordinators displaying assigned events,
    registered totals, checked-in numbers, and live attendance percentages.
    """
    return AttendanceService.get_coordinator_dashboard(db, current_user)


@router.get("/attendance")
def get_live_attendance(
    event_id: int = Query(..., description="ID of the event to view attendance for"),
    current_user: User = Depends(require_role(RoleEnum.COORDINATOR, RoleEnum.ADMIN)),
    db: Session = Depends(get_db)
):
    """List of all participants checked into a specific event with timestamps."""
    return AttendanceService.get_event_attendance_list(db, event_id)
