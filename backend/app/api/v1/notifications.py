from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.notification import NotificationResponse, NotificationUnreadCount
from app.services.notification_service import (
    get_user_notifications,
    mark_notifications_read,
    get_unread_count
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class MarkReadRequest(BaseModel):
    notification_ids: Optional[List[int]] = None


@router.get("", response_model=List[NotificationResponse])
def list_my_notifications(
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifs = get_user_notifications(db, current_user.id, limit=limit, unread_only=unread_only)
    return [NotificationResponse.model_validate(n) for n in notifs]


@router.post("/mark-read")
def mark_read(
    req: MarkReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = mark_notifications_read(db, current_user.id, req.notification_ids)
    return {"success": True, "count": updated}


@router.get("/unread-count", response_model=NotificationUnreadCount)
def unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = get_unread_count(db, current_user.id)
    return NotificationUnreadCount(unread_count=count)
