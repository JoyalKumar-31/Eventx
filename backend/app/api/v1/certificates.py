from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.enums import UserRole
from app.models.certificate import Certificate
from app.models.user import User
from app.schemas.certificate import CertificateResponse, CertificateVerifyResponse
from app.services.certificate_service import generate_pdf_certificate_bytes

router = APIRouter(prefix="/certificates", tags=["Certificates"])


def format_cert_response(c: Certificate) -> CertificateResponse:
    return CertificateResponse(
        id=c.id,
        certificate_number=c.certificate_number,
        registration_id=c.registration_id,
        user_id=c.user_id,
        participant_name=c.user.full_name,
        event_id=c.event_id,
        event_title=c.event.title,
        award_title=c.award_title,
        issue_date=c.issue_date,
        verification_hash=c.verification_hash,
        template_type=c.template_type,
        pdf_url=f"/api/certificates/{c.id}/download"
    )


@router.get("/my", response_model=List[CertificateResponse])
def get_my_certificates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    certs = db.query(Certificate).filter(Certificate.user_id == current_user.id).order_by(Certificate.issue_date.desc()).all()
    return [format_cert_response(c) for c in certs]


@router.get("/{certificate_id}/download")
def download_certificate_pdf(
    certificate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cert = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    if current_user.role != UserRole.ADMIN and cert.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to download this certificate")

    pdf_bytes = generate_pdf_certificate_bytes(
        participant_name=cert.user.full_name,
        event_title=cert.event.title,
        award_title=cert.award_title,
        cert_number=cert.certificate_number,
        issue_date=cert.issue_date,
        verification_hash=cert.verification_hash
    )

    filename = f"{cert.certificate_number}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/verify/{query_hash_or_number}", response_model=CertificateVerifyResponse)
def verify_certificate_authenticity(
    query_hash_or_number: str,
    db: Session = Depends(get_db)
):
    """
    Public endpoint to verify authentic university fest certificates.
    Accepts certificate number or cryptographic verification hash.
    """
    cleaned = query_hash_or_number.strip()
    cert = db.query(Certificate).filter(
        (Certificate.verification_hash == cleaned) | (Certificate.certificate_number.ilike(cleaned))
    ).first()

    if not cert:
        return CertificateVerifyResponse(
            is_valid=False,
            message="No authentic certificate matching this identifier was found in the database."
        )

    college = None
    if cert.user.student_profile:
        college = cert.user.student_profile.college_name

    return CertificateVerifyResponse(
        is_valid=True,
        certificate_number=cert.certificate_number,
        participant_name=cert.user.full_name,
        event_title=cert.event.title,
        award_title=cert.award_title,
        issue_date=cert.issue_date,
        college_name=college,
        message="Authentic certificate verified against official database."
    )
