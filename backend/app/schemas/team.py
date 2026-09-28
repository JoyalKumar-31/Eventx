from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.student import UserBasicOut


class TeamMemberOut(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    college: Optional[str] = None
    joined_at: datetime


class TeamOut(BaseModel):
    id: int
    name: str
    event_id: int
    event_name: str
    code: str
    is_finalized: bool
    leader: UserBasicOut
    members: List[TeamMemberOut] = []
    created_at: datetime


class TeamCreate(BaseModel):
    name: str
    event_id: int


class TeamJoin(BaseModel):
    code: str


class TeamInvitationCreate(BaseModel):
    email: str


class TeamInvitationOut(BaseModel):
    id: int
    team_id: int
    team_name: str
    event_name: str
    status: str
    created_at: datetime
