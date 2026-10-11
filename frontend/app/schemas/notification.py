from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import NotificationType
# hi


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    message: str
    type: NotificationType
    link: Optional[str] = None
    is_read: bool
    created_at: datetime


class NotificationUnreadCount(BaseModel):
    unread_count: int
