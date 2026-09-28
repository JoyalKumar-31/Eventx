from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.registration import RegistrationCreate, RegistrationInitResponse, RegistrationOut
from app.services.registration_service import RegistrationService

router = APIRouter(prefix="/registrations", tags=["Registrations"])


@router.post("", response_model=RegistrationInitResponse, status_code=status.HTTP_201_CREATED)
def register_for_event(
    reg_in: RegistrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register for an event with validations for deadlines, capacity,
    duplicate check, and team requirements.
    """
    return RegistrationService.create_registration(db, current_user, reg_in)


@router.get("/my", response_model=List[RegistrationOut])
def get_my_registrations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all event registrations for the logged-in user."""
    return RegistrationService.get_my_registrations(db, current_user)
