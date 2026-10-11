from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import AnnouncementTarget


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    target_audience: AnnouncementTarget = AnnouncementTarget.ALL
    is_pinned: bool = False


class AnnouncementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    target_audience: AnnouncementTarget
    is_pinned: bool
    created_by_name: str
    created_at: datetime
