from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.registration import RegistrationStatus


class RegistrationCreate(BaseModel):
    event_id: int
    team_id: Optional[int] = None


class RegistrationInitResponse(BaseModel):
    registration_id: int
    status: str
    amount: float
    message: str


class RegistrationOut(BaseModel):
    id: int
    event_id: int
    event_name: str
    event_date: str
    event_time: str
    venue_name: str
    category_name: str
    status: RegistrationStatus
    amount: float
    team_id: Optional[int] = None
    team_name: Optional[str] = None
    has_pass: bool = False
    pass_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
