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
    Looks up participant/team registration status and payment details.
    """
    reg_key = reg_id.upper().strip()
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
    Validates QR code entry pass at fest gates.
    """
    code = pass_code.upper().strip()
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
