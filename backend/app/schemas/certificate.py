from typing import Optional
from pydantic import BaseModel


class CertificateOut(BaseModel):
    id: int
    certificate_id: str
    participant_name: str
    college: Optional[str] = None
    event_name: str
    event_date: str
    title: str
    issue_date: str
    is_verified: bool
    pdf_url: Optional[str] = None


class CertificateVerifyOut(BaseModel):
    is_valid: bool
    certificate_id: str
    participant_name: Optional[str] = None
    college: Optional[str] = None
    event_name: Optional[str] = None
    issue_date: Optional[str] = None
    message: str
