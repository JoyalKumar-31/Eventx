from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import RegistrationStatus, TeamStatus, TeamMemberRole


class TeamMemberResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_email: str
    role: TeamMemberRole
    joined_at: datetime


class TeamCreate(BaseModel):
    name: str
    event_id: int


class TeamJoinRequest(BaseModel):
    invite_code: str


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    event_id: int
    leader_id: int
    invite_code: str
    status: TeamStatus
    created_at: datetime
    members: List[TeamMemberResponse] = []


class RegistrationCreate(BaseModel):
    event_id: int
    team_id: Optional[int] = None


class RegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    registration_number: str
    event_id: int
    event_title: str
    user_id: int
    participant_name: str
    participant_email: str
    team_id: Optional[int] = None
    team_name: Optional[str] = None
    status: RegistrationStatus
    registered_at: datetime
    qr_code_hash: str
    payment_status: Optional[str] = None
    entry_status: Optional[str] = None


class QREntryPassResponse(BaseModel):
    registration_id: int
    registration_number: str
    event_id: int
    event_title: str
    participant_name: str
    participant_email: str
    venue_name: Optional[str] = None
    venue_building: Optional[str] = None
    start_time: datetime
    status: RegistrationStatus
    qr_code_hash: str
    qr_image_base64: str
