from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, RoleEnum
from app.schemas.admin import AdminDashboardOut, AdminAnalyticsOut
from app.schemas.auth import UserOut
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin & Analytics"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that strictly enforces Admin role."""
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/dashboard", response_model=AdminDashboardOut)
def get_admin_dashboard(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Consolidated admin dashboard statistics: total users, active events,
    gross revenue, overall attendance percentage, and recent registrations.
    """
    return AdminService.get_dashboard(db)


@router.get("/analytics", response_model=AdminAnalyticsOut)
def get_admin_analytics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    In-depth fest analytics: daily registration timelines, category revenue share,
    top performing colleges, and event capacity fill rates.
    """
    return AdminService.get_analytics(db)


@router.get("/users", response_model=List[UserOut])
def get_users_list(
    search: Optional[str] = Query(None, description="Search by name, email or college"),
    role: Optional[str] = Query(None, description="Filter by role (STUDENT, COORDINATOR, JUDGE, ADMIN)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    User management directory.
    Strictly role-protected: Students attempting access receive 'Admin access required'.
    """
    return AdminService.get_users_list(db, search=search, role=role, limit=limit, offset=offset)


@router.put("/users/{id}/role", response_model=UserOut)
def update_user_role(
    id: int,
    new_role: RoleEnum = Query(..., description="Target role to assign"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Assign or modify user roles across the platform."""
    return AdminService.update_user_role(db, id, new_role)
