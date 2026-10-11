import hashlib
import io
import os
import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.models.certificate import Certificate
from app.models.registration import Registration
from app.models.event import Event
from app.models.user import User


def generate_certificate_hash(cert_number: str, user_id: int, event_id: int) -> str:
    raw = f"{cert_number}:{user_id}:{event_id}:{uuid.uuid4().hex}:{datetime.now(timezone.utc).isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def generate_pdf_certificate_bytes(
    participant_name: str,
    event_title: str,
    award_title: str,
    cert_number: str,
    issue_date: datetime,
    verification_hash: str
) -> bytes:
    """Generate an authentic, high-resolution landscape PDF certificate."""
    buffer = io.BytesIO()
    # Landscape letter: 792 x 612 pt
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # 1. Outer Border & Inner Gold Border
    c.setStrokeColor(colors.HexColor("#0f172a"))  # Slate 900
    c.setLineWidth(5)
    c.rect(20, 20, width - 40, height - 40)

    c.setStrokeColor(colors.HexColor("#f59e0b"))  # Amber 500
    c.setLineWidth(1.5)
    c.rect(26, 26, width - 52, height - 52)

    # Corner Accents
    c.setFillColor(colors.HexColor("#f59e0b"))
    accent_size = 14
    c.rect(20, height - 20 - accent_size, accent_size, accent_size, fill=1, stroke=0)
    c.rect(width - 20 - accent_size, height - 20 - accent_size, accent_size, accent_size, fill=1, stroke=0)
    c.rect(20, 20, accent_size, accent_size, fill=1, stroke=0)
    c.rect(width - 20 - accent_size, 20, accent_size, accent_size, fill=1, stroke=0)

    # 2. Header / University Fest Emblem
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#4f46e5"))  # Indigo 600
    c.drawCentredString(width / 2, height - 75, "ANNUAL INTER-COLLEGIATE FESTIVAL")

    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawCentredString(width / 2, height - 120, "CERTIFICATE OF EXCELLENCE")

    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.setLineWidth(1)
    c.line(width / 2 - 180, height - 135, width / 2 + 180, height - 135)

    # 3. Award subtitle
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawCentredString(width / 2, height - 165, "THIS IS PROUDLY PRESENTED TO")

    # 4. Participant Name
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(colors.HexColor("#1e293b"))
    c.drawCentredString(width / 2, height - 215, participant_name.upper())

    c.setStrokeColor(colors.HexColor("#f59e0b"))
    c.setLineWidth(1.5)
    c.line(width / 2 - 150, height - 225, width / 2 + 150, height - 225)

    # 5. Citation Text
    c.setFont("Helvetica", 13)
    c.setFillColor(colors.HexColor("#334155"))
    citation = f"for outstanding achievement and participation in '{event_title}'"
    c.drawCentredString(width / 2, height - 265, citation)

    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(colors.HexColor("#4338ca"))
    c.drawCentredString(width / 2, height - 295, f"Award: {award_title}")

    # 6. Verification & Signatures section
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.setLineWidth(0.8)

    # Left signature line
    c.line(100, 110, 260, 110)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#1e293b"))
    c.drawCentredString(180, 95, "Faculty Coordinator")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawCentredString(180, 80, "Fest Organizing Committee")

    # Right signature line
    c.line(width - 260, 110, width - 100, 110)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#1e293b"))
    c.drawCentredString(width - 180, 95, "Dean of Student Affairs")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawCentredString(width - 180, 80, "University Campus")

    # Center Verification badge & hash
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawCentredString(width / 2, 90, f"Certificate ID: {cert_number}")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.drawCentredString(width / 2, 75, f"Issued Date: {issue_date.strftime('%B %d, %Y')} | Verification Hash: {verification_hash[:16]}...")
    c.drawCentredString(width / 2, 60, "Verify online at college-fest portal with Certificate ID")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()


def issue_certificate_for_registration(
    db: Session,
    registration_id: int,
    award_title: str = "Certificate of Participation"
) -> Certificate:
    reg = db.query(Registration).filter(Registration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")

    existing = db.query(Certificate).filter(Certificate.registration_id == registration_id).first()
    if existing:
        return existing

    cert_number = f"FEST-CERT-{reg.event_id:03d}-{reg.id:04d}-{uuid.uuid4().hex[:6].upper()}"
    v_hash = generate_certificate_hash(cert_number, reg.user_id, reg.event_id)

    cert = Certificate(
        certificate_number=cert_number,
        registration_id=reg.id,
        user_id=reg.user_id,
        event_id=reg.event_id,
        award_title=award_title,
        verification_hash=v_hash,
        template_type="STANDARD"
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert
