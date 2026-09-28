"""
tools/team_tools.py - Participant & Team Management Tools
"""

from typing import Dict, Any
from .event_tools import get_event_details

# Sample database of participants and registered teams
TEAMS_DB = {
    "REG-101": {
        "team_name": "CyberKnights",
        "event": "TechSprint 24-Hour Hackathon",
        "leader": "Aarav Sharma",
        "members": ["Aarav Sharma", "Priya Verma", "Rohan Mehta"],
        "payment_status": "PAID",
        "qr_pass_code": "PASS-CYBER-101",
        "attendance_checked_in": True
    },
    "REG-102": {
        "team_name": "MechaTitans",
        "event": "RoboWars: Clash of Titans",
        "leader": "Aditya Singh",
        "members": ["Aditya Singh", "Sneha Patel"],
        "payment_status": "PENDING_UPI_VERIFICATION",
        "qr_pass_code": "PASS-MECHA-102",
        "attendance_checked_in": False
    }
}


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
        from app.core.database import SessionLocal
        from app.models.registration import Registration
        from app.models.pass_attendance import FestPass, Attendance
        from app.models.team import Team
        from app.models.user import User

        db = SessionLocal()
        try:
            # Check numeric ID (e.g. "REG-1" or "1")
            num_part = ''.join(c for c in reg_key if c.isdigit())
            db_reg = None
            if num_part:
                db_reg = db.query(Registration).filter(Registration.id == int(num_part)).first()

            # If not found by ID, search by team name or user email/name
            if not db_reg:
                db_reg = db.query(Registration).join(Registration.user).filter(
                    (User.email.ilike(f"%{reg_id}%")) | (User.full_name.ilike(f"%{reg_id}%"))
                ).first()

            if db_reg:
                team_name = db_reg.team.name if db_reg.team else (db_reg.user.full_name if db_reg.user else "Individual")
                leader_name = db_reg.team.leader.full_name if (db_reg.team and db_reg.team.leader) else (db_reg.user.full_name if db_reg.user else "Participant")
                members_count = len(db_reg.team.members) if db_reg.team else 1
                payment_status = db_reg.payment.status.value if db_reg.payment else db_reg.status.value
                qr_pass_code = db_reg.fest_pass.qr_token if db_reg.fest_pass else "NOT_ISSUED"
                is_checked_in = (db_reg.attendance is not None and db_reg.attendance.status.value == "CHECKED_IN")

                return {
                    "found": True,
                    "registration_id": f"REG-{db_reg.id}",
                    "team_name": team_name,
                    "event": db_reg.event.name if db_reg.event else "N/A",
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

    # Fallback to in-memory TEAMS_DB
    if reg_key in TEAMS_DB:
        team = TEAMS_DB[reg_key]
        return {
            "found": True,
            "registration_id": reg_key,
            "team_name": team["team_name"],
            "event": team["event"],
            "leader": team["leader"],
            "members_count": len(team["members"]),
            "payment_status": team["payment_status"],
            "qr_pass": team["qr_pass_code"],
            "attendance": "Checked In" if team["attendance_checked_in"] else "Not Checked In"
        }
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
        from app.core.database import SessionLocal
        from app.models.pass_attendance import FestPass, PassStatus, AttendanceStatus
        from app.models.registration import Registration, RegistrationStatus

        db = SessionLocal()
        try:
            # Query by qr_token or pass id
            num_part = ''.join(c for c in code if c.isdigit())
            db_pass = db.query(FestPass).filter(
                (FestPass.qr_token.ilike(code)) |
                (FestPass.qr_token.ilike(f"%{code}%")) |
                (FestPass.id == int(num_part) if num_part else False)
            ).first()

            if db_pass:
                reg = db_pass.registration
                team_or_user = reg.team.name if (reg and reg.team) else (reg.user.full_name if (reg and reg.user) else "Participant")
                event_name = reg.event.name if (reg and reg.event) else "Fest Event"

                if db_pass.status == PassStatus.REVOKED:
                    return {
                        "granted": False,
                        "reason": "Entry Denied: This Fest Pass has been revoked by administration."
                    }

                if reg and reg.status != RegistrationStatus.CONFIRMED:
                    return {
                        "granted": False,
                        "reason": f"Payment pending ({reg.status.value})! Please clear dues at the registration desk."
                    }

                return {
                    "granted": True,
                    "team_name": team_or_user,
                    "event": event_name,
                    "pass_id": db_pass.id,
                    "message": f"Entry Approved for {team_or_user}! Pass {db_pass.qr_token} verified."
                }
        finally:
            db.close()
    except Exception:
        pass

    # Fallback to TEAMS_DB
    for reg_id, team in TEAMS_DB.items():
        if team["qr_pass_code"] == code:
            if team["payment_status"] != "PAID":
                return {
                    "granted": False,
                    "reason": "Payment pending! Please clear UPI dues at the registration counter."
                }
            return {
                "granted": True,
                "team_name": team["team_name"],
                "event": team["event"],
                "message": f"Entry Approved for {team['team_name']}!"
            }
    return {
        "granted": False,
        "reason": f"Invalid or unrecognized pass code '{pass_code}'."
    }
