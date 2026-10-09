from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, model_validator
from app.models.enums import AttendanceStatus


class QRScanRequest(BaseModel):
    qr_payload: Optional[str] = None
    qr_hash: Optional[str] = None
    event_id: Optional[int] = None
    round_id: Optional[int] = None
    remarks: Optional[str] = None

    @model_validator(mode="after")
    def resolve_payload(self):
        if not self.qr_payload and not self.qr_hash:
            raise ValueError("qr_payload or qr_hash is required")
        if not self.qr_payload:
            self.qr_payload = self.qr_hash
        return self


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
    registration: Optional[Dict[str, Any]] = None


class AttendanceStats(BaseModel):
    total_registrations: int
    total_attended: int
    attendance_percentage: float
