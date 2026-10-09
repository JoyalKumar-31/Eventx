import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.enums import UserRole, EventStatus, RegistrationStatus, TeamStatus
from app.models.event import Event
from app.models.registration import Registration, Team, TeamMember
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

    user_data = {
        "id": reg.user.id,
        "full_name": reg.user.full_name,
        "email": reg.user.email,
        "role": reg.user.role.value if hasattr(reg.user.role, "value") else str(reg.user.role),
        "avatar_url": getattr(reg.user, "avatar_url", None)
    } if reg.user else None

    event_data = {
        "id": reg.event.id,
        "title": reg.event.title,
        "slug": reg.event.slug,
        "registration_fee": reg.event.registration_fee,
        "start_time": reg.event.start_time,
        "start_date": reg.event.start_time,
        "end_time": reg.event.end_time,
        "category": {
            "id": reg.event.category.id,
            "name": reg.event.category.name
        } if reg.event and reg.event.category else None,
        "venue": {
            "id": reg.event.venue.id,
            "name": reg.event.venue.name,
            "building": reg.event.venue.building
        } if reg.event and reg.event.venue else None,
        "is_team_event": reg.event.is_team_event if reg.event else False,
        "min_team_size": reg.event.min_team_size if reg.event else 1,
        "max_team_size": reg.event.max_team_size if reg.event else 1,
        "event_format": "TEAM" if (reg.event and reg.event.is_team_event) else "SOLO",
    } if reg.event else None

    team_data = {
        "id": reg.team.id,
        "name": reg.team.name,
        "invite_code": reg.team.invite_code,
        "leader_id": reg.team.leader_id
    } if reg.team else None

    fee = reg.event.registration_fee if reg.event else 0.0
    p_status = latest_payment.status.value if latest_payment else ("FREE" if fee == 0 else "UNPAID")
    e_status = latest_attendance.entry_status.value if latest_attendance else "NOT_ENTERED"

    return RegistrationResponse(
        id=reg.id,
        registration_number=reg.registration_number,
        event_id=reg.event_id,
        event_title=reg.event.title if reg.event else f"Event #{reg.event_id}",
        user_id=reg.user_id,
        participant_name=reg.user.full_name if reg.user else f"User #{reg.user_id}",
        participant_email=reg.user.email if reg.user else "",
        team_id=reg.team_id,
        team_name=reg.team.name if reg.team else None,
        status=reg.status,
        registered_at=reg.registered_at,
        created_at=reg.registered_at,
        qr_code_hash=reg.qr_code_hash,
        payment_status=p_status,
        entry_status=e_status,
        registration_fee=fee,
        user=user_data,
        event=event_data,
        team=team_data
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

    # Team logic
    if event.is_team_event:
        if not req.team_id:
            raise HTTPException(status_code=400, detail="This is a team event. Please select or create your squad before registering.")
        team = db.query(Team).filter(Team.id == req.team_id, Team.event_id == event.id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team squad not found for this event")

        is_member = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == current_user.id).first()
        if not is_member:
            raise HTTPException(status_code=403, detail="You must be an active squad member to register.")

        if len(team.members) < event.min_team_size:
            raise HTTPException(
                status_code=400,
                detail=f"Team requires at least {event.min_team_size} members to register (current members: {len(team.members)})."
            )

        # Initial status based on fee
        initial_status = RegistrationStatus.CONFIRMED if event.registration_fee == 0 else RegistrationStatus.PENDING_PAYMENT

        # Register all team members who don't have registration yet
        caller_registration = None
        for member in team.members:
            existing = db.query(Registration).filter(
                Registration.event_id == event.id,
                Registration.user_id == member.user_id
            ).first()

            if not existing:
                reg_num = f"REG-{event.id:03d}-{uuid.uuid4().hex[:6].upper()}"
                qr_token = generate_qr_hash(reg_num, event.id, member.user_id)
                reg_entry = Registration(
                    registration_number=reg_num,
                    event_id=event.id,
                    user_id=member.user_id,
                    team_id=team.id,
                    status=initial_status,
                    qr_code_hash=qr_token
                )
                db.add(reg_entry)
                event.current_participants += 1

                create_notification(
                    db,
                    user_id=member.user_id,
                    title="Squad Registered!",
                    message=f"Your squad '{team.name}' has been registered for '{event.title}'. Status: {initial_status.value}.",
                    link="/student/passes"
                )

                if member.user_id == current_user.id:
                    caller_registration = reg_entry
            else:
                existing.team_id = team.id
                if member.user_id == current_user.id:
                    caller_registration = existing

        team.status = TeamStatus.COMPLETE
        db.commit()
        if caller_registration:
            db.refresh(caller_registration)
            return format_reg_response(caller_registration)

    # Solo Registration
    existing = db.query(Registration).filter(
        Registration.event_id == event.id,
        Registration.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You have already registered for this event")

    reg_number = f"REG-{event.id:03d}-{uuid.uuid4().hex[:6].upper()}"
    qr_hash = generate_qr_hash(reg_number, event.id, current_user.id)
    initial_status = RegistrationStatus.CONFIRMED if event.registration_fee == 0 else RegistrationStatus.PENDING_PAYMENT

    registration = Registration(
        registration_number=reg_number,
        event_id=event.id,
        user_id=current_user.id,
        team_id=None,
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
        link="/student/registrations"
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

    if current_user.role not in [UserRole.ADMIN, UserRole.EVENT_COORDINATOR] and reg.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to view this entry pass")

    payload_str = build_qr_pass_payload(reg.registration_number, reg.qr_code_hash, reg.event_id)
    qr_b64 = generate_qr_image_base64(payload_str)

    venue = reg.event.venue if reg.event else None

    return QREntryPassResponse(
        registration_id=reg.id,
        registration_number=reg.registration_number,
        event_id=reg.event_id,
        event_title=reg.event.title if reg.event else "Fest Event",
        participant_name=reg.user.full_name if reg.user else "Participant",
        participant_email=reg.user.email if reg.user else "",
        venue_name=venue.name if venue else "Main Campus",
        venue_building=venue.building if venue else "Campus Arena",
        start_time=reg.event.start_time if reg.event else datetime.now(timezone.utc),
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

    regs = db.query(Registration).filter(Registration.event_id == event_id).order_by(Registration.registered_at.desc()).all()
    return [format_reg_response(r) for r in regs]
