import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.user import User, RoleEnum
from app.models.certificate import Certificate
from app.schemas.certificate import CertificateOut, CertificateVerifyOut
from app.services.certificate_service import CertificateService

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.get("", response_model=List[CertificateOut])
def get_my_certificates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all certificates earned by the authenticated student."""
    return CertificateService.get_user_certificates(db, current_user)


@router.get("/verify/{certificate_id}", response_model=CertificateVerifyOut)
def verify_certificate(certificate_id: str, db: Session = Depends(get_db)):
    """
    Public verification endpoint to authenticate FESTORA certificates.
    Used by employers, recruiters, and colleges.
    """
    return CertificateService.verify_certificate(db, certificate_id)


@router.get("/{certificate_id}/download")
def download_certificate_pdf(certificate_id: str, db: Session = Depends(get_db)):
    """Generate on-the-fly and download official high-resolution PDF certificate."""
    cert = db.query(Certificate).filter(Certificate.certificate_id == certificate_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    pdf_path = CertificateService.generate_pdf(cert)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"Festora_Certificate_{certificate_id}.pdf"
    )


@router.post("/generate/{registration_id}", response_model=CertificateOut, status_code=status.HTTP_201_CREATED)
def generate_certificate_for_registration(
    registration_id: int,
    current_user: User = Depends(require_role(RoleEnum.COORDINATOR, RoleEnum.ADMIN)),
    db: Session = Depends(get_db)
):
    """Generate certificate for an event participant."""
    cert = CertificateService.generate_certificate(db, registration_id)
    certs = CertificateService.get_user_certificates(db, cert.user)
    return next((c for c in certs if c.certificate_id == cert.certificate_id), None)
