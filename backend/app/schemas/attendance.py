from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.enums import AttendanceStatus


class QRScanRequest(BaseModel):
    qr_payload: str
    event_id: Optional[int] = None
    round_id: Optional[int] = None
    remarks: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: int
    registration_id: int
    event_id: int
    participant_name: str
    participant_email: str
    event_title: str
    entry_status: AttendanceStatus
    scanned_at: datetime
    remarks: Optional[str] = None


class AttendanceStats(BaseModel):
    total_registrations: int
    total_attended: int
    attendance_percentage: float
