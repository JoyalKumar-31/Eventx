import os
import secrets
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from app.core.config import settings
from app.models.certificate import Certificate
from app.models.registration import Registration, RegistrationStatus
from app.models.pass_attendance import Attendance
from app.models.event import Event
from app.models.user import User
from app.schemas.certificate import CertificateOut, CertificateVerifyOut


class CertificateService:
    @staticmethod
    def generate_certificate(db: Session, registration_id: int) -> Certificate:
        reg = db.query(Registration).options(
            joinedload(Registration.user),
            joinedload(Registration.event),
            joinedload(Registration.attendance)
        ).filter(Registration.id == registration_id).first()

        if not reg:
            raise HTTPException(status_code=404, detail="Registration not found")

        # Check existing certificate
        existing = db.query(Certificate).filter(Certificate.registration_id == reg.id).first()
        if existing:
            return existing

        cert_id = f"FEST-{datetime.now().year}-{reg.event_id}-{secrets.token_hex(3).upper()}"

        cert = Certificate(
            certificate_id=cert_id,
            registration_id=reg.id,
            user_id=reg.user_id,
            event_id=reg.event_id,
            title="Certificate of Participation",
            pdf_url=f"/api/certificates/{cert_id}/download",
            is_verified=True
        )
        db.add(cert)
        db.commit()
        db.refresh(cert)
        return cert

    @staticmethod
    def get_user_certificates(db: Session, user: User) -> List[CertificateOut]:
        certs = db.query(Certificate).options(
            joinedload(Certificate.user),
            joinedload(Certificate.event)
        ).filter(Certificate.user_id == user.id).all()

        results = []
        for c in certs:
            ev = c.event
            results.append(
                CertificateOut(
                    id=c.id,
                    certificate_id=c.certificate_id,
                    participant_name=c.user.full_name,
                    college=c.user.college,
                    event_name=ev.name if ev else "Festora Event",
                    event_date=str(ev.event_date) if ev else str(datetime.now().date()),
                    title=c.title,
                    issue_date=c.issue_date.strftime("%d %B %Y"),
                    is_verified=c.is_verified,
                    pdf_url=c.pdf_url
                )
            )
        return results

    @staticmethod
    def verify_certificate(db: Session, certificate_id: str) -> CertificateVerifyOut:
        cert = db.query(Certificate).options(
            joinedload(Certificate.user),
            joinedload(Certificate.event)
        ).filter(Certificate.certificate_id == certificate_id.strip()).first()

        if not cert or not cert.is_verified:
            return CertificateVerifyOut(
                is_valid=False,
                certificate_id=certificate_id,
                message="Certificate not found or could not be verified"
            )

        return CertificateVerifyOut(
            is_valid=True,
            certificate_id=cert.certificate_id,
            participant_name=cert.user.full_name,
            college=cert.user.college,
            event_name=cert.event.name,
            issue_date=cert.issue_date.strftime("%d %B %Y"),
            message="Verified authentic FESTORA official certificate"
        )

    @staticmethod
    def generate_pdf(cert: Certificate) -> str:
        """
        Generates a certificate PDF and returns the file path.
        """
        cert_dir = os.path.join(settings.CERTIFICATES_DIR)
        os.makedirs(cert_dir, exist_ok=True)
        pdf_path = os.path.join(cert_dir, f"{cert.certificate_id}.pdf")

        # Landscape letter
        c = canvas.Canvas(pdf_path, pagesize=landscape(letter))
        width, height = landscape(letter)

        # Border
        c.setStrokeColor(colors.HexColor("#4F46E5"))
        c.setLineWidth(5)
        c.rect(20, 20, width - 40, height - 40)

        c.setStrokeColor(colors.HexColor("#C7D2FE"))
        c.setLineWidth(1.5)
        c.rect(28, 28, width - 56, height - 56)

        # Title
        c.setFont("Helvetica-Bold", 32)
        c.setFillColor(colors.HexColor("#1E1B4B"))
        c.drawCentredString(width / 2.0, height - 90, "FESTORA 2026")

        c.setFont("Helvetica", 14)
        c.setFillColor(colors.HexColor("#6B7280"))
        c.drawCentredString(width / 2.0, height - 120, "ANNUAL NATIONAL INTER-COLLEGIATE TECH & CULTURAL FESTIVAL")

        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(colors.HexColor("#4338CA"))
        c.drawCentredString(width / 2.0, height - 170, cert.title.upper())

        # Body text
        c.setFont("Helvetica", 13)
        c.setFillColor(colors.HexColor("#374151"))
        c.drawCentredString(width / 2.0, height - 220, "This is proudly presented to")

        # Participant Name
        c.setFont("Helvetica-Bold", 26)
        c.setFillColor(colors.HexColor("#111827"))
        c.drawCentredString(width / 2.0, height - 260, cert.user.full_name)

        # College
        college_text = f"from {cert.user.college}" if cert.user.college else ""
        c.setFont("Helvetica-Oblique", 14)
        c.setFillColor(colors.HexColor("#4B5563"))
        c.drawCentredString(width / 2.0, height - 290, college_text)

        # Event participation
        event_name = cert.event.name if cert.event else "Festora Competition"
        c.setFont("Helvetica", 14)
        c.setFillColor(colors.HexColor("#374151"))
        c.drawCentredString(
            width / 2.0,
            height - 330,
            f"for successful participation in the event '{event_name}'"
        )

        # Certificate ID & verification URL
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#9CA3AF"))
        c.drawString(45, 50, f"Certificate ID: {cert.certificate_id}")
        c.drawRightString(width - 45, 50, f"Issued: {cert.issue_date.strftime('%d %B %Y')}")

        c.showPage()
        c.save()

        return pdf_path
