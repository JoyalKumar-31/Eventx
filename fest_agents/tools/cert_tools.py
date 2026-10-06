"""
tools/cert_tools.py - Results, Certificate Text Generation, and Announcements
"""

from typing import Dict, Any


def generate_certificate_text(recipient_name: str, event_name: str, position: str = "Participant") -> Dict[str, Any]:
    """
    Generates standardized certificate verification wording for winners and participants.
    """
    cert_id = f"CERT-FEST-{abs(hash(recipient_name + event_name)) % 100000:05d}"
    
    if "winner" in position.lower() or "1st" in position.lower():
        title = "CERTIFICATE OF EXCELLENCE (WINNER)"
        statement = (
            f"This is to proudly certify that {recipient_name} has secured FIRST POSITION in the event "
            f"'{event_name}' at the Annual College Tech & Cultural Fest."
        )
    elif "runner" in position.lower() or "2nd" in position.lower():
        title = "CERTIFICATE OF MERIT (RUNNER UP)"
        statement = (
            f"This is to proudly certify that {recipient_name} has secured SECOND POSITION in the event "
            f"'{event_name}' at the Annual College Tech & Cultural Fest."
        )
    else:
        title = "CERTIFICATE OF PARTICIPATION"
        statement = (
            f"This is to certify that {recipient_name} has enthusiastically participated in the event "
            f"'{event_name}' at the Annual College Tech & Cultural Fest."
        )
    
    return {
        "certificate_id": cert_id,
        "title": title,
        "recipient": recipient_name,
        "event": event_name,
        "position": position,
        "certificate_body": statement
    }


def draft_announcement(title: str, message: str, priority: str = "NORMAL") -> Dict[str, Any]:
    """
    Drafts a broadcast notification for the fest website and mobile app feed.
    """
    return {
        "status": "DRAFTED",
        "priority": priority.upper(),
        "broadcast_title": f"[FEST UPDATE] {title}",
        "broadcast_message": message,
        "channels": ["Push Notification", "Portal Banner", "Notice Board"]
    }
