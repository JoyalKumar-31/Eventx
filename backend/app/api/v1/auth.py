from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserDetailResponse,
    UserInfo
)
from app.services.auth_service import register_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserInfo, status_code=status.HTTP_201_CREATED)
def register(
    req: UserRegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Registers a real user account with hashed password and associated role profile.
    """
    client_ip = request.client.host if request.client else None
    user = register_user(db=db, req=req, ip_address=client_ip)
    return UserInfo.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(
    req: UserLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticates user credentials against the database.
    Returns signed JWT access token and user role.
    No role selection allowed at login.
    """
    client_ip = request.client.host if request.client else None
    token_response = authenticate_user(
        db=db,
        email=req.email,
        password=req.password,
        ip_address=client_ip
    )
    return token_response


@router.get("/me", response_model=UserDetailResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns current authenticated user details and profile.
    """
    return UserDetailResponse.model_validate(current_user)


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Logs out the authenticated user.
    """
    return {"success": True, "message": "Logged out successfully"}
