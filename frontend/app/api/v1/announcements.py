from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, get_current_user_optional, require_role
from app.models.enums import UserRole, AnnouncementTarget
from app.models.announcement import Announcement
from app.models.user import User
from app.schemas.announcement import AnnouncementCreate, AnnouncementResponse
from app.services.audit_service import log_action

router = APIRouter(prefix="/announcements", tags=["Announcements"])


@router.get("", response_model=List[AnnouncementResponse])
def list_announcements(
    target: Optional[AnnouncementTarget] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    query = db.query(Announcement)

    # Filter based on target audience if user role is known
    if not current_user:
        query = query.filter(Announcement.target_audience == AnnouncementTarget.ALL)
    elif current_user.role != UserRole.ADMIN:
        allowed_targets = [AnnouncementTarget.ALL]
        if current_user.role == UserRole.STUDENT:
            allowed_targets.append(AnnouncementTarget.STUDENTS)
        elif current_user.role == UserRole.EVENT_COORDINATOR:
            allowed_targets.append(AnnouncementTarget.COORDINATORS)
        elif current_user.role == UserRole.JUDGE:
            allowed_targets.append(AnnouncementTarget.JUDGES)
        elif current_user.role == UserRole.SPONSOR:
            allowed_targets.append(AnnouncementTarget.SPONSORS)
        query = query.filter(Announcement.target_audience.in_(allowed_targets))

    announcements = query.order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).all()
    return [
        AnnouncementResponse(
            id=a.id,
            title=a.title,
            content=a.content,
            target_audience=a.target_audience,
            is_pinned=a.is_pinned,
            created_by_name=a.created_by.full_name,
            created_at=a.created_at
        )
        for a in announcements
    ]


@router.post("", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
def create_announcement(
    req: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.EVENT_COORDINATOR))
):
    ann = Announcement(
        title=req.title.strip(),
        content=req.content.strip(),
        target_audience=req.target_audience,
        is_pinned=req.is_pinned,
        created_by_user_id=current_user.id
    )
    db.add(ann)
    db.commit()
    db.refresh(ann)

    log_action(
        db,
        action="ANNOUNCEMENT_CREATED",
        entity_type="Announcement",
        entity_id=str(ann.id),
        user_id=current_user.id,
        new_values={"title": ann.title, "target": ann.target_audience.value}
    )

    return AnnouncementResponse(
        id=ann.id,
        title=ann.title,
        content=ann.content,
        target_audience=ann.target_audience,
        is_pinned=ann.is_pinned,
        created_by_name=current_user.full_name,
        created_at=ann.created_at
    )


@router.delete("/{announcement_id}", status_code=status.HTTP_200_OK)
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    ann = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    db.delete(ann)
    db.commit()
    return {"success": True, "message": "Announcement deleted"}
