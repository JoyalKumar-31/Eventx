"""
tools/team_tools.py - Participant & Team Management Tools
"""

from typing import Dict, Any, Optional, List
from .event_tools import get_event_details



def validate_team_size(event_name: str, member_count: int) -> Dict[str, Any]:
    """
    Validates if a team's member count satisfies event rules.
    """
    event = get_event_details(event_name)
    if not event:
        return {
            "valid": False,
            "message": f"Event '{event_name}' was not found in fest catalog."
        }
    
    min_size = event["min_team_size"]
    max_size = event["max_team_size"]
    
    if member_count < min_size:
        return {
            "valid": False,
            "message": f"Team too small! {event['title']} requires at least {min_size} members (you provided {member_count})."
        }
    elif member_count > max_size:
        return {
            "valid": False,
            "message": f"Team too large! {event['title']} allows at most {max_size} members (you provided {member_count})."
        }
    else:
        return {
            "valid": True,
            "message": f"Valid team size ({member_count} members) for {event['title']}. Allowed: {min_size}-{max_size}."
        }


def check_registration_status(reg_id: str) -> Dict[str, Any]:
    """
    Looks up participant/team registration status and payment details from MySQL or fallback DB.
    """
    reg_key = reg_id.upper().strip()

    # Try live MySQL database first
    try:
        from app.db.session import SessionLocal
        from app.models.registration import Registration
        from app.models.user import User

        db = SessionLocal()
        try:
            # Check numeric ID (e.g. "REG-1" or "1")
            num_part = ''.join(c for c in reg_key if c.isdigit())
            db_reg = None
            if num_part:
                db_reg = db.query(Registration).filter(
                    (Registration.registration_number.ilike(f"%{reg_key}%")) |
                    (Registration.id == int(num_part))
                ).first()

            # If not found by ID, search by registration number, team name, or user email/name
            if not db_reg:
                db_reg = db.query(Registration).join(Registration.user).filter(
                    (Registration.registration_number.ilike(f"%{reg_id}%")) |
                    (User.email.ilike(f"%{reg_id}%")) |
                    (User.full_name.ilike(f"%{reg_id}%"))
                ).first()

            if db_reg:
                team_name = db_reg.team.name if db_reg.team else (db_reg.user.full_name if db_reg.user else "Individual Competitor")
                leader_name = db_reg.team.leader.full_name if (db_reg.team and db_reg.team.leader) else (db_reg.user.full_name if db_reg.user else "Participant")
                members_count = len(db_reg.team.members) if db_reg.team else 1
                payment_status = db_reg.status.value
                qr_pass_code = db_reg.qr_code_hash or f"PASS-{db_reg.id}"
                is_checked_in = bool(db_reg.attendance_records and len(db_reg.attendance_records) > 0)

                return {
                    "found": True,
                    "registration_id": db_reg.registration_number or f"REG-{db_reg.id}",
                    "team_name": team_name,
                    "event": db_reg.event.title if db_reg.event else "N/A",
                    "leader": leader_name,
                    "members_count": members_count,
                    "payment_status": payment_status,
                    "qr_pass": qr_pass_code,
                    "attendance": "Checked In" if is_checked_in else "Not Checked In"
                }
        finally:
            db.close()
    except Exception:
        pass

    return {
        "found": False,
        "message": f"No registration record found for ID '{reg_id}'."
    }


def verify_qr_entry_pass(pass_code: str) -> Dict[str, Any]:
    """
    Validates QR code entry pass at fest gates against MySQL or fallback DB.
    """
    code = pass_code.upper().strip()

    # Try live MySQL database first
    try:
        from app.db.session import SessionLocal
        from app.models.registration import Registration
        from app.models.enums import RegistrationStatus

        db = SessionLocal()
        try:
            # Query by qr_code_hash or registration_number or numeric id
            num_part = ''.join(c for c in code if c.isdigit())
            db_reg = db.query(Registration).filter(
                (Registration.qr_code_hash.ilike(code)) |
                (Registration.qr_code_hash.ilike(f"%{code}%")) |
                (Registration.registration_number.ilike(code)) |
                (Registration.id == int(num_part) if num_part else False)
            ).first()

            if db_reg:
                team_or_user = db_reg.team.name if db_reg.team else (db_reg.user.full_name if db_reg.user else "Participant")
                event_name = db_reg.event.title if db_reg.event else "Fest Event"

                if db_reg.status == RegistrationStatus.CANCELLED:
                    return {
                        "granted": False,
                        "reason": "Entry Denied: This registration has been cancelled or revoked."
                    }

                if db_reg.status == RegistrationStatus.PENDING_PAYMENT:
                    return {
                        "granted": False,
                        "reason": "Payment pending! Please complete fee payment at the registration counter."
                    }

                return {
                    "granted": True,
                    "team_name": team_or_user,
                    "event": event_name,
                    "pass_id": db_reg.id,
                    "message": f"Entry Approved for {team_or_user}! Pass {db_reg.registration_number} verified."
                }
        finally:
            db.close()
    except Exception:
        pass

    return {
        "granted": False,
        "reason": f"Invalid or unrecognized pass code '{pass_code}'."
    }


def register_student_for_event(
    event_name_or_id: str,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    team_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes actual registration for a student into an event directly in MySQL database.
    Creates Registration record, assigns unique Registration ID, generates QR pass, and updates participant count.
    """
    import uuid
    import hashlib
    try:
        from app.db.session import SessionLocal
        from app.models.user import User
        from app.models.event import Event
        from app.models.registration import Registration, Team, TeamMember
        from app.models.enums import RegistrationStatus, EventStatus, TeamStatus, TeamMemberRole
        from app.services.audit_service import log_action

        db = SessionLocal()
        try:
            # 1. Resolve student user
            user = None
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
            if not user and user_email:
                user = db.query(User).filter(User.email.ilike(user_email.strip())).first()

            if not user:
                return {
                    "success": False,
                    "error": "NOT_LOGGED_IN",
                    "message": "You must be logged in as a Student to register for events. Please log in or sign up at [/register](/register)."
                }

            # 2. Resolve Event
            clean_input = str(event_name_or_id).strip().lower()
            db_events = db.query(Event).filter(Event.status != EventStatus.DRAFT).all()
            matched_event = None

            # Numeric ID match
            if clean_input.isdigit():
                matched_event = db.query(Event).filter(Event.id == int(clean_input)).first()

            if not matched_event:
                # Substring or exact match
                for ev in db_events:
                    ev_title = ev.title.lower()
                    if clean_input == ev_title or clean_input in ev_title or ev_title in clean_input:
                        matched_event = ev
                        break

            if not matched_event:
                # Fuzzy keyword match
                words = [w for w in clean_input.split() if len(w) > 3 and w not in ["register", "want", "into", "event", "please"]]
                for ev in db_events:
                    ev_title = ev.title.lower()
                    if any(w in ev_title for w in words):
                        matched_event = ev
                        break

            if not matched_event:
                avail_titles = [f"• **{e.title}** ({e.category.name if e.category else 'General'})" for e in db_events[:5]]
                return {
                    "success": False,
                    "error": "EVENT_NOT_FOUND",
                    "message": f"Could not find an event matching '{event_name_or_id}'. Available events:\n" + "\n".join(avail_titles)
                }

            # 3. Check existing registration
            existing_reg = db.query(Registration).filter(
                Registration.event_id == matched_event.id,
                Registration.user_id == user.id
            ).first()

            if existing_reg:
                venue_name = matched_event.venue.name if matched_event.venue else "Campus Arena"
                is_free = (float(matched_event.registration_fee or 0) == 0.0)
                has_paid = any(p.status.value == "SUCCESS" for p in existing_reg.payments) if existing_reg.payments else False
                is_cleared = is_free or (existing_reg.status == RegistrationStatus.CONFIRMED and has_paid)

                if is_cleared:
                    pass_info = (
                        f"• **Status**: `CONFIRMED`\n"
                        f"• **Pass Code**: `{existing_reg.qr_code_hash}`\n\n"
                        f"View your digital QR pass in your [Student Passes Portal](/student/passes) or [My Registrations](/student/registrations)."
                    )
                    pass_val = existing_reg.qr_code_hash
                else:
                    fee_val = f"₹{float(matched_event.registration_fee):.0f}"
                    pass_info = (
                        f"• **Status**: `PENDING PAYMENT` (Fee: {fee_val})\n"
                        f"• **Pass Code**: 🔒 Locked (Payment Pending)\n\n"
                        f"⚠️ **Payment Required**: Please go to [My Registrations](/student/registrations) and click **Pay {fee_val}** to complete payment and unlock your digital QR code."
                    )
                    pass_val = "🔒 Locked (Payment Pending)"

                return {
                    "success": True,
                    "already_registered": True,
                    "registration_number": existing_reg.registration_number,
                    "event_title": matched_event.title,
                    "status": "CONFIRMED" if is_cleared else "PENDING_PAYMENT",
                    "qr_pass": pass_val,
                    "venue": venue_name,
                    "message": (
                        f"You are already registered for **{matched_event.title}**!\n\n"
                        f"• **Registration Number**: `{existing_reg.registration_number}`\n"
                        f"• **Venue**: {venue_name}\n"
                        + pass_info
                    )
                }

            # 4. Handle Team creation if team event
            created_team = None
            if matched_event.is_team_event and matched_event.min_team_size > 1:
                t_name = team_name or f"Squad {user.full_name.split()[0]}"
                invite_code = f"TEAM-{matched_event.id}-{uuid.uuid4().hex[:5].upper()}"
                created_team = Team(
                    name=t_name,
                    event_id=matched_event.id,
                    leader_id=user.id,
                    invite_code=invite_code,
                    status=TeamStatus.FORMING
                )
                db.add(created_team)
                db.flush()

                # Add leader as member
                leader_member = TeamMember(
                    team_id=created_team.id,
                    user_id=user.id,
                    role=TeamMemberRole.LEADER
                )
                db.add(leader_member)

            # 5. Create Registration Record
            reg_num = f"REG-{matched_event.id:03d}-{uuid.uuid4().hex[:6].upper()}"
            qr_hash = f"PASS-{hashlib.sha256(f'{reg_num}:{matched_event.id}:{user.id}:{uuid.uuid4()}'.encode()).hexdigest()[:12].upper()}"
            is_free = (float(matched_event.registration_fee or 0) == 0.0)
            status_val = RegistrationStatus.CONFIRMED if is_free else RegistrationStatus.PENDING_PAYMENT

            new_reg = Registration(
                registration_number=reg_num,
                event_id=matched_event.id,
                user_id=user.id,
                team_id=created_team.id if created_team else None,
                status=status_val,
                qr_code_hash=qr_hash
            )
            db.add(new_reg)
            matched_event.current_participants = (matched_event.current_participants or 0) + 1
            db.commit()
            db.refresh(new_reg)

            try:
                log_action(
                    db,
                    action="AI_AGENT_EVENT_REGISTRATION",
                    entity_type="Registration",
                    entity_id=str(new_reg.id),
                    user_id=user.id,
                    new_values={"event": matched_event.title, "registration_number": reg_num, "status": status_val.value}
                )
            except Exception:
                pass

            start_str = matched_event.start_time.strftime("%d %b, %I:%M %p") if matched_event.start_time else "TBA"
            venue_str = matched_event.venue.name if matched_event.venue else "Campus Arena"
            fee_str = f"₹{float(matched_event.registration_fee):.0f}" if matched_event.registration_fee > 0 else "Free Entry"

            if is_free:
                msg = (
                    f"🎉 **Registration Confirmed for {matched_event.title}!**\n\n"
                    f"• **Registration ID**: `{reg_num}`\n"
                    f"• **Participant**: {user.full_name}\n"
                    f"• **Event Category**: {matched_event.category.name if matched_event.category else 'General'}\n"
                    f"• **Date & Time**: {start_str}\n"
                    f"• **Venue**: {venue_str}\n"
                    f"• **Fee**: Free Entry (Status: `CONFIRMED`)\n"
                    f"• **Digital Pass Key**: `{qr_hash}`\n"
                    + (f"• **Team Name**: {created_team.name} (Share Invite Code: `{created_team.invite_code}`)\n" if created_team else "")
                    + f"\nYour QR entry pass has been generated! You can access it anytime in your [Student Passes](/student/passes) or [My Registrations](/student/registrations)."
                )
                pass_key_output = qr_hash
            else:
                msg = (
                    f"📋 **Registration Initiated for {matched_event.title}!**\n\n"
                    f"• **Registration ID**: `{reg_num}`\n"
                    f"• **Participant**: {user.full_name}\n"
                    f"• **Event Category**: {matched_event.category.name if matched_event.category else 'General'}\n"
                    f"• **Date & Time**: {start_str}\n"
                    f"• **Venue**: {venue_str}\n"
                    f"• **Registration Fee**: {fee_str}\n"
                    f"• **Registration Status**: `PENDING PAYMENT`\n"
                    f"• **Digital QR Pass**: 🔒 Locked (Payment Pending)\n"
                    + (f"• **Team Name**: {created_team.name} (Share Invite Code: `{created_team.invite_code}`)\n" if created_team else "")
                    + f"\n⚠️ **Payment Pending**: Because this is a paid event ({fee_str}), your registration is in **Pending Payment** status. "
                    f"Please navigate to [My Registrations](/student/registrations) and click **Pay {fee_str}**. "
                    f"Once your payment is completed, your official digital QR entry pass will be unlocked and available in My Registrations!"
                )
                pass_key_output = "🔒 Locked (Payment Pending)"

            return {
                "success": True,
                "already_registered": False,
                "registration_number": reg_num,
                "event_title": matched_event.title,
                "category": matched_event.category.name if matched_event.category else "General",
                "venue": venue_str,
                "schedule": start_str,
                "fee": fee_str,
                "is_paid": is_free,
                "status": status_val.value,
                "qr_pass": pass_key_output,
                "team_name": created_team.name if created_team else "Individual",
                "invite_code": created_team.invite_code if created_team else None,
                "message": msg
            }
        finally:
            db.close()
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "message": f"Could not complete registration due to an unexpected database error: {str(exc)}"
        }


def get_user_registrations(user_id: Optional[int] = None, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches all live festival registrations and passes for a given student from MySQL.
    """
    try:
        from app.db.session import SessionLocal
        from app.models.user import User
        from app.models.registration import Registration

        db = SessionLocal()
        try:
            user = None
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
            if not user and user_email:
                user = db.query(User).filter(User.email.ilike(user_email.strip())).first()

            if not user:
                return []

            regs = db.query(Registration).filter(Registration.user_id == user.id).all()
            output = []
            from app.models.enums import RegistrationStatus
            for r in regs:
                start_str = r.event.start_time.strftime("%d %b, %I:%M %p") if (r.event and r.event.start_time) else "TBA"
                venue_str = r.event.venue.name if (r.event and r.event.venue) else "Campus Arena"
                fee = float(r.event.registration_fee or 0) if r.event else 0.0
                has_paid = any(p.status.value == "SUCCESS" for p in r.payments) if r.payments else False
                is_cleared = (fee == 0.0) or (r.status == RegistrationStatus.CONFIRMED and has_paid)

                output.append({
                    "registration_number": r.registration_number,
                    "event_title": r.event.title if r.event else "N/A",
                    "status": "CONFIRMED" if is_cleared else "PENDING_PAYMENT",
                    "is_paid": is_cleared,
                    "fee": fee,
                    "qr_pass": r.qr_code_hash if is_cleared else "🔒 Locked (Payment Pending)",
                    "venue": venue_str,
                    "time": start_str,
                    "team_name": r.team.name if r.team else "Individual",
                    "registered_at": r.registered_at.strftime("%d %b %Y") if r.registered_at else "N/A"
                })
            return output
        finally:
            db.close()
    except Exception:
        return []


def check_in_participant(reg_id_or_num: str, coordinator_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Marks gate check-in and attendance for a participant in MySQL.
    """
    try:
        from app.db.session import SessionLocal
        from app.models.registration import Registration
        from app.models.attendance import Attendance
        from datetime import datetime, timezone

        db = SessionLocal()
        try:
            clean = reg_id_or_num.strip().upper()
            reg = db.query(Registration).filter(
                (Registration.registration_number.ilike(f"%{clean}%")) |
                (Registration.qr_code_hash.ilike(f"%{clean}%"))
            ).first()

            if not reg:
                return {"success": False, "message": f"Registration '{reg_id_or_num}' not found."}

            existing_att = db.query(Attendance).filter(Attendance.registration_id == reg.id).first()
            if existing_att:
                return {
                    "success": True,
                    "already_checked_in": True,
                    "message": f"Participant **{reg.user.full_name if reg.user else 'Attendee'}** was already checked in at {existing_att.checked_in_at}."
                }

            att = Attendance(
                registration_id=reg.id,
                event_id=reg.event_id,
                checked_in_at=datetime.now(timezone.utc),
                scanned_by_id=coordinator_id
            )
            db.add(att)
            db.commit()

            return {
                "success": True,
                "already_checked_in": False,
                "participant": reg.user.full_name if reg.user else "Attendee",
                "event": reg.event.title if reg.event else "Fest Event",
                "message": f"✅ Check-in recorded for **{reg.user.full_name if reg.user else 'Attendee'}** for event **{reg.event.title}**."
            }
        finally:
            db.close()
    except Exception as exc:
        return {"success": False, "message": f"Check-in failed: {str(exc)}"}

