import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.enums import UserRole, EventStatus, RegistrationStatus, TeamStatus
from app.models.event import Event
from app.models.registration import Registration, Team
from app.models.attendance import Attendance
from app.models.payment import Payment
from app.models.user import User
from app.schemas.registration import RegistrationCreate, RegistrationResponse, QREntryPassResponse
from app.services.qr_service import generate_qr_hash, generate_qr_image_base64, build_qr_pass_payload
from app.services.notification_service import create_notification
from app.services.audit_service import log_action

router = APIRouter(prefix="/registrations", tags=["Registrations"])


def format_reg_response(reg: Registration) -> RegistrationResponse:
    latest_payment = reg.payments[-1] if reg.payments else None
    latest_attendance = reg.attendance_records[-1] if reg.attendance_records else None

    return RegistrationResponse(
        id=reg.id,
        registration_number=reg.registration_number,
        event_id=reg.event_id,
        event_title=reg.event.title,
        user_id=reg.user_id,
        participant_name=reg.user.full_name,
        participant_email=reg.user.email,
        team_id=reg.team_id,
        team_name=reg.team.name if reg.team else None,
        status=reg.status,
        registered_at=reg.registered_at,
        qr_code_hash=reg.qr_code_hash,
        payment_status=latest_payment.status.value if latest_payment else ("FREE" if reg.event.registration_fee == 0 else "UNPAID"),
        entry_status=latest_attendance.entry_status.value if latest_attendance else "NOT_ENTERED"
    )


@router.post("", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_for_event(
    req: RegistrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT, UserRole.ADMIN))
):
    event = db.query(Event).filter(Event.id == req.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.status not in [EventStatus.PUBLISHED, EventStatus.ONGOING]:
        raise HTTPException(status_code=400, detail=f"Registrations are not open for this event (status: {event.status.value})")

    # Deadline validation
    deadline = event.registration_deadline if event.registration_deadline.tzinfo else event.registration_deadline.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > deadline:
        raise HTTPException(status_code=400, detail="Registration deadline for this event has passed")

    # Capacity validation
    if event.current_participants >= event.max_participants:
        raise HTTPException(status_code=400, detail="This event has reached maximum capacity")

    # Duplicate check
    existing = db.query(Registration).filter(
        Registration.event_id == event.id,
        Registration.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You have already registered for this event")

    # Team check if team event
    if event.is_team_event:
        if not req.team_id:
            raise HTTPException(status_code=400, detail="This is a team event. Please provide a valid team ID or create a team.")
        team = db.query(Team).filter(Team.id == req.team_id, Team.event_id == event.id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found for this event")

    # Unique registration number & QR token
    reg_number = f"REG-{event.id:03d}-{uuid.uuid4().hex[:6].upper()}"
    qr_hash = generate_qr_hash(reg_number, event.id, current_user.id)

    # Initial status based on fee
    initial_status = RegistrationStatus.CONFIRMED if event.registration_fee == 0 else RegistrationStatus.PENDING_PAYMENT

    registration = Registration(
        registration_number=reg_number,
        event_id=event.id,
        user_id=current_user.id,
        team_id=req.team_id,
        status=initial_status,
        qr_code_hash=qr_hash
    )
    db.add(registration)
    event.current_participants += 1

    db.commit()
    db.refresh(registration)

    log_action(
        db,
        action="EVENT_REGISTRATION",
        entity_type="Registration",
        entity_id=str(registration.id),
        user_id=current_user.id,
        new_values={"registration_number": reg_number, "status": initial_status.value}
    )

    create_notification(
        db,
        user_id=current_user.id,
        title="Registration Received",
        message=f"You are registered for '{event.title}'. Status: {initial_status.value}.",
        link=f"/student/registrations"
    )

    return format_reg_response(registration)


@router.get("/my", response_model=List[RegistrationResponse])
def get_my_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    regs = db.query(Registration).filter(Registration.user_id == current_user.id).order_by(Registration.registered_at.desc()).all()
    return [format_reg_response(r) for r in regs]


@router.get("/{registration_id}/pass", response_model=QREntryPassResponse)
def get_qr_entry_pass(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reg = db.query(Registration).filter(Registration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")

    if current_user.role != UserRole.ADMIN and reg.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to view this entry pass")

    payload_str = build_qr_pass_payload(reg.registration_number, reg.qr_code_hash, reg.event_id)
    qr_b64 = generate_qr_image_base64(payload_str)

    venue = reg.event.venue

    return QREntryPassResponse(
        registration_id=reg.id,
        registration_number=reg.registration_number,
        event_id=reg.event_id,
        event_title=reg.event.title,
        participant_name=reg.user.full_name,
        participant_email=reg.user.email,
        venue_name=venue.name if venue else "Main Campus",
        venue_building=venue.building if venue else "Campus Arena",
        start_time=reg.event.start_time,
        status=reg.status,
        qr_code_hash=reg.qr_code_hash,
        qr_image_base64=qr_b64
    )


@router.get("/event/{event_id}", response_model=List[RegistrationResponse])
def list_event_participants(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN, UserRole.JUDGE))
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.role == UserRole.EVENT_COORDINATOR and event.coordinator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized: Not coordinator for this event")

    regs = db.query(Registration).filter(Registration.event_id == event_id).all()
    return [format_reg_response(r) for r in regs]
