from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import (
    UserRegister, UserLogin, TokenResponse, RefreshTokenRequest,
    UserOut, UserProfileUpdate, UserInterestCreate
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Register a new student, coordinator, judge or sponsor."""
    return AuthService.register(db, user_in)


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate with email and password to receive JWT tokens."""
    return AuthService.login(db, credentials)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Obtain a new access and refresh token pair."""
    return AuthService.refresh(db, req.refresh_token)


@router.get("/me", response_model=UserOut)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get profile of currently logged-in user."""
    return current_user


@router.put("/profile", response_model=UserOut)
def update_profile(
    profile_in: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user personal profile details."""
    return AuthService.update_profile(db, current_user, profile_in)


@router.post("/interests", response_model=List[str])
def set_interests(
    interests_in: UserInterestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set favorite event categories for personalized recommendations."""
    AuthService.set_user_interests(db, current_user.id, interests_in.categories)
    return AuthService.get_user_interests(db, current_user.id)


@router.get("/interests", response_model=List[str])
def get_interests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's saved interests."""
    return AuthService.get_user_interests(db, current_user.id)
