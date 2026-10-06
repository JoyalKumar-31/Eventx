from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CertificateResponse(BaseModel):
    id: int
    certificate_number: str
    registration_id: int
    user_id: int
    participant_name: str
    event_id: int
    event_title: str
    award_title: str
    issue_date: datetime
    verification_hash: str
    template_type: str
    pdf_url: Optional[str] = None


class CertificateVerifyResponse(BaseModel):
    is_valid: bool
    certificate_number: Optional[str] = None
    participant_name: Optional[str] = None
    event_title: Optional[str] = None
    award_title: Optional[str] = None
    issue_date: Optional[datetime] = None
    college_name: Optional[str] = None
    message: str = "Certificate verified successfully"
