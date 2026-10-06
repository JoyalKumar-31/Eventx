from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.enums import UserRole
from app.models.user import User, StudentProfile, CoordinatorProfile, JudgeProfile, SponsorProfile
from app.schemas.auth import UserDetailResponse, UserInfo
from app.schemas.admin import UserRoleUpdate, UserStatusUpdate
from app.services.audit_service import log_action

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserDetailResponse])
def list_users(
    role: Optional[UserRole] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        search_filter = f"%{search}%"
        query = query.filter((User.full_name.ilike(search_filter)) | (User.email.ilike(search_filter)))

    users = query.order_by(User.id.desc()).offset(skip).limit(limit).all()
    return [UserDetailResponse.model_validate(u) for u in users]


@router.get("/coordinators", response_model=List[UserInfo])
def list_coordinators(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List event coordinators for assignments and directory."""
    coordinators = db.query(User).filter(User.role == UserRole.EVENT_COORDINATOR, User.is_active == True).all()
    return [UserInfo.model_validate(c) for c in coordinators]


@router.get("/judges", response_model=List[UserInfo])
def list_judges(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    """List available judges for assignment."""
    judges = db.query(User).filter(User.role == UserRole.JUDGE, User.is_active == True).all()
    return [UserInfo.model_validate(j) for j in judges]


@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized to view this user profile")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserDetailResponse.model_validate(user)


@router.put("/{user_id}/role", response_model=UserDetailResponse)
def update_user_role(
    user_id: int,
    req: UserRoleUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_role = user.role.value
    user.role = req.role
    db.commit()
    db.refresh(user)

    log_action(
        db,
        action="ROLE_UPDATED",
        entity_type="User",
        entity_id=str(user.id),
        user_id=admin_user.id,
        old_values={"role": old_role},
        new_values={"role": user.role.value}
    )

    return UserDetailResponse.model_validate(user)


@router.put("/{user_id}/status", response_model=UserDetailResponse)
def update_user_status(
    user_id: int,
    req: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_status = user.is_active
    user.is_active = req.is_active
    db.commit()
    db.refresh(user)

    log_action(
        db,
        action="USER_STATUS_UPDATED",
        entity_type="User",
        entity_id=str(user.id),
        user_id=admin_user.id,
        old_values={"is_active": old_status},
        new_values={"is_active": user.is_active}
    )

    return UserDetailResponse.model_validate(user)
