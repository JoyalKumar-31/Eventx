from typing import List, Optional
from pydantic import BaseModel


class FestPassOut(BaseModel):
    id: int
    registration_id: int
    participant: str
    event: str
    date: str
    time: str
    venue: str
    status: str
    qr_token: str
    qr_image_url: Optional[str] = None


class AttendanceScanRequest(BaseModel):
    qr_token: str
    event_id: Optional[int] = None


class AttendanceScanResponse(BaseModel):
    success: bool
    participant: str
    event: str
    attendance: str
    time: str
    checked_in_count: int
    total_registered: int
    message: str


class CoordinatorEventSummary(BaseModel):
    id: int
    name: str
    category: str
    event_date: str
    time: str
    venue: str
    registered_count: int
    checked_in_count: int
    attendance_rate: float


class CoordinatorDashboardOut(BaseModel):
    coordinator_name: str
    assigned_events: List[CoordinatorEventSummary]
    total_registered: int
    total_checked_in: int
    overall_attendance_rate: float
