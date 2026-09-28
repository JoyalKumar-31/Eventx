from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.pass_attendance import FestPassOut
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/passes", tags=["Fest Passes"])


@router.get("/{id}", response_model=FestPassOut)
def get_pass_by_id(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve fest pass details by pass ID or registration ID.
    Includes participant info, event schedule, venue, and QR code token.
    """
    return AttendanceService.get_pass_by_id(db, id, current_user)
