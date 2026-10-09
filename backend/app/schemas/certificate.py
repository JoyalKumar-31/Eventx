from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, model_validator


class CertificateResponse(BaseModel):
    id: int
    certificate_number: str
    registration_id: int
    user_id: int
    participant_name: str
    event_id: int
    event_title: str
    award_title: str
    certificate_type: Optional[str] = None
    issue_date: datetime
    issued_at: Optional[datetime] = None
    verification_hash: str
    template_type: str
    pdf_url: Optional[str] = None
    event: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def populate_aliases(self):
        if not self.issued_at:
            self.issued_at = self.issue_date
        if not self.certificate_type:
            self.certificate_type = self.award_title or self.template_type
        return self


class CertificateVerifyResponse(BaseModel):
    is_valid: bool
    id: Optional[int] = None
    certificate_number: Optional[str] = None
    participant_name: Optional[str] = None
    event_title: Optional[str] = None
    award_title: Optional[str] = None
    certificate_type: Optional[str] = None
    issue_date: Optional[datetime] = None
    college_name: Optional[str] = None
    verification_hash: Optional[str] = None
    pdf_url: Optional[str] = None
    message: str = "Certificate verified successfully"
