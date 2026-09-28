import secrets
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.registration import Registration, RegistrationStatus
from app.models.event import Event
from app.models.team import Team, TeamMember
from app.models.user import User
from app.models.pass_attendance import FestPass, PassStatus
from app.models.notification import Notification
from app.schemas.registration import RegistrationCreate, RegistrationInitResponse, RegistrationOut
from app.utils.qr import generate_qr_code_image, generate_qr_code_base64


class RegistrationService:
    @staticmethod
    def create_registration(
        db: Session,
        user: User,
        reg_in: RegistrationCreate
    ) -> RegistrationInitResponse:
        # 1. Check event exists and is active
        event = db.query(Event).filter(Event.id == reg_in.event_id, Event.is_active == True).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found or inactive")

        # 2. Check registration deadline
        now = datetime.now()
        if event.registration_deadline and now > event.registration_deadline:
            raise HTTPException(status_code=400, detail="Registration deadline for this event has passed")

        # 3. Check capacity
        if event.registered_count >= event.capacity:
            raise HTTPException(status_code=400, detail="Event registration is full")

        # 4. Check duplicate registration for individual
        existing_reg = db.query(Registration).filter(
            Registration.user_id == user.id,
            Registration.event_id == event.id,
            Registration.status.in_([RegistrationStatus.CONFIRMED, RegistrationStatus.PENDING_PAYMENT])
        ).first()
        if existing_reg:
            raise HTTPException(
                status_code=400,
                detail="You already have an active registration for this event"
            )

        # 5. Check team requirements
        team = None
        if event.min_team_size > 1:
            if not reg_in.team_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"This is a team event (min {event.min_team_size} members). Please create or select a team first."
                )
            team = db.query(Team).options(joinedload(Team.members)).filter(Team.id == reg_in.team_id).first()
            if not team:
                raise HTTPException(status_code=404, detail="Specified team does not exist")
            if team.event_id != event.id:
                raise HTTPException(status_code=400, detail="Team does not belong to this event")
            if len(team.members) < event.min_team_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"Team requires at least {event.min_team_size} members (currently {len(team.members)})"
                )

        fee = float(event.registration_fee)
        is_free = fee <= 0.0

        # 6. Create Registration record
        reg = Registration(
            user_id=user.id,
            event_id=event.id,
            team_id=team.id if team else None,
            status=RegistrationStatus.CONFIRMED if is_free else RegistrationStatus.PENDING_PAYMENT,
            amount=fee
        )
        db.add(reg)
        db.commit()
        db.refresh(reg)

        # 7. If free event, immediately confirm, increment capacity and generate pass
        if is_free:
            event.registered_count += 1
            qr_token = f"FEST-PASS-{reg.id}-{secrets.token_hex(8).upper()}"
            qr_url = generate_qr_code_image(qr_token)

            fest_pass = FestPass(
                registration_id=reg.id,
                qr_token=qr_token,
                qr_image_url=qr_url,
                status=PassStatus.ACTIVE
            )
            db.add(fest_pass)

            # Notification
            db.add(
                Notification(
                    user_id=user.id,
                    title=f"Registration Confirmed: {event.name}",
                    message=f"You are successfully registered for {event.name}. Your Fest Pass is ready!",
                    type="REGISTRATION",
                    link=f"/passes/{reg.id}"
                )
            )
            db.commit()

            return RegistrationInitResponse(
                registration_id=reg.id,
                status="CONFIRMED",
                amount=fee,
                message="Registration confirmed! Your fest pass is ready."
            )

        # If payment required
        return RegistrationInitResponse(
            registration_id=reg.id,
            status="PAYMENT_PENDING",
            amount=fee,
            message="Registration initiated. Please complete payment to confirm your spot."
        )

    @staticmethod
    def get_my_registrations(db: Session, user: User) -> List[RegistrationOut]:
        registrations = db.query(Registration).options(
            joinedload(Registration.event).joinedload(Event.venue),
            joinedload(Registration.event).joinedload(Event.category),
            joinedload(Registration.team),
            joinedload(Registration.fest_pass)
        ).filter(Registration.user_id == user.id).order_by(Registration.created_at.desc()).all()

        results = []
        for r in registrations:
            ev = r.event
            has_pass = r.fest_pass is not None and r.status == RegistrationStatus.CONFIRMED
            results.append(
                RegistrationOut(
                    id=r.id,
                    event_id=ev.id,
                    event_name=ev.name,
                    event_date=str(ev.event_date),
                    event_time=str(ev.start_time),
                    venue_name=ev.venue.name if ev.venue else "Campus",
                    category_name=ev.category.name if ev.category else "General",
                    status=r.status,
                    amount=float(r.amount),
                    team_id=r.team_id,
                    team_name=r.team.name if r.team else None,
                    has_pass=has_pass,
                    pass_id=r.fest_pass.id if has_pass else None,
                    created_at=r.created_at
                )
            )
        return results
