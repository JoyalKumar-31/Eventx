from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import (
    UserRegisterRequest,
    StudentRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserDetailResponse,
    UserInfo
)
from app.schemas.application import (
    CoordinatorApplyRequest,
    CoordinatorApplicationResponse,
    JudgeApplyRequest,
    JudgeApplicationResponse
)
from app.services.auth_service import register_user, authenticate_user
from app.services.application_service import apply_coordinator, apply_judge

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


# --- Public Role Application Endpoints ---

@router.post("/apply/coordinator", response_model=CoordinatorApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_for_coordinator(
    req: CoordinatorApplyRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Allows faculty, staff, or senior students to apply for Event Coordinator privileges.
    Application starts in PENDING status and does NOT grant coordinator access until Admin approves.
    """
    client_ip = request.client.host if request.client else None
    app = apply_coordinator(db=db, req=req, ip_address=client_ip)
    return CoordinatorApplicationResponse.model_validate(app)


@router.post("/apply/judge", response_model=JudgeApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_for_judge(
    req: JudgeApplyRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Allows industry experts, domain veterans, and professors to apply for Fest Judge privileges.
    Application starts in PENDING status and does NOT grant judge access until Admin approves.
    """
    client_ip = request.client.host if request.client else None
    app = apply_judge(db=db, req=req, ip_address=client_ip)
    return JudgeApplicationResponse.model_validate(app)


@router.get("/application/status")
def check_application_status(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Allows applicants to check the progress of their coordinator or judge application.
    """
    email_clean = email.lower().strip()
    from app.models.application import CoordinatorApplication, JudgeApplication

    coord_app = db.query(CoordinatorApplication).filter(CoordinatorApplication.email == email_clean).order_by(CoordinatorApplication.created_at.desc()).first()
    judge_app = db.query(JudgeApplication).filter(JudgeApplication.email == email_clean).order_by(JudgeApplication.created_at.desc()).first()

    return {
        "email": email_clean,
        "coordinator_application": {
            "id": coord_app.id,
            "status": coord_app.status.value,
            "submitted_at": coord_app.created_at,
            "admin_notes": coord_app.admin_notes
        } if coord_app else None,
        "judge_application": {
            "id": judge_app.id,
            "status": judge_app.status.value,
            "submitted_at": judge_app.created_at,
            "admin_notes": judge_app.admin_notes
        } if judge_app else None,
    }

