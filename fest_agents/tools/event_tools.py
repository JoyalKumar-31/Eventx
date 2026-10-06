"""
tools/event_tools.py - Event Management and Scheduling Tools
Integrated with live MySQL database and fallback dataset.
"""

from typing import Dict, Any, List, Optional

# Fallback in-memory database of fest events
FEST_EVENTS_DB = {
    "hackathon": {
        "title": "TechSprint 24-Hour Hackathon",
        "category": "Technical",
        "venue": "Main Computer Lab (Block A)",
        "start_time": "Day 1, 10:00 AM",
        "end_time": "Day 2, 10:00 AM",
        "min_team_size": 2,
        "max_team_size": 4,
        "registration_fee": 500,  # in INR
        "rules": [
            "All code must be written during the 24 hours.",
            "Pre-built templates or existing repos are disqualified.",
            "Every team must submit code via GitHub with commits."
        ]
    },
    "codesprint": {
        "title": "Code Sprint",
        "category": "Technical",
        "venue": "Computer Lab 2",
        "start_time": "28 Oct, 10:00 AM",
        "end_time": "28 Oct, 01:00 PM",
        "min_team_size": 1,
        "max_team_size": 1,
        "registration_fee": 150,
        "rules": [
            "Individual participation only. No collaboration.",
            "Languages supported: C++, Java, Python, JavaScript, Rust.",
            "Rankings based on test cases passed and execution speed."
        ]
    },
    "robowars": {
        "title": "RoboWars: Clash of Titans",
        "category": "Robotics",
        "venue": "Open Air Amphitheatre",
        "start_time": "Day 2, 02:00 PM",
        "end_time": "Day 2, 06:00 PM",
        "min_team_size": 1,
        "max_team_size": 5,
        "registration_fee": 800,
        "rules": [
            "Bot weight must not exceed 15 kg.",
            "Wired or wireless remote controls are permitted.",
            "No flame throwers or corrosive chemicals allowed."
        ]
    },
    "battle_of_bands": {
        "title": "Battle of the Bands",
        "category": "Cultural",
        "venue": "Main Auditorium",
        "start_time": "Day 1, 05:00 PM",
        "end_time": "Day 1, 09:00 PM",
        "min_team_size": 3,
        "max_team_size": 8,
        "registration_fee": 500,
        "rules": [
            "Time limit is 15 minutes including setup.",
            "Drum kit will be provided, bands must bring their own guitars & keys."
        ]
    },
    "codeclash": {
        "title": "CodeClash: Speed Coding Contest",
        "category": "Technical",
        "venue": "Seminar Hall 2",
        "start_time": "Day 1, 02:00 PM",
        "end_time": "Day 1, 04:00 PM",
        "min_team_size": 1,
        "max_team_size": 1,
        "registration_fee": 150,
        "rules": [
            "Individual participation only.",
            "Languages supported: C++, Java, Python.",
            "Rankings based on test cases passed and time taken."
        ]
    }
}


def get_all_events() -> List[Dict[str, Any]]:
    """Returns a list of all registered fest events with summary details."""
    try:
        from app.core.database import SessionLocal
        from app.models.event import Event
        db = SessionLocal()
        try:
            db_events = db.query(Event).filter(Event.is_active == True).all()
            if db_events:
                summary = []
                for ev in db_events:
                    summary.append({
                        "event_key": str(ev.id),
                        "title": ev.name,
                        "category": ev.category.name if ev.category else "General",
                        "venue": ev.venue.name if ev.venue else "Campus",
                        "time": f"{ev.event_date} {ev.start_time.strftime('%I:%M %p')} - {ev.end_time.strftime('%I:%M %p')}",
                        "team_size": f"{ev.min_team_size}-{ev.max_team_size} members",
                        "fee": f"Rs. {float(ev.registration_fee):.0f}"
                    })
                return summary
        finally:
            db.close()
    except Exception:
        pass

    # Fallback to local catalog
    summary = []
    for key, event in FEST_EVENTS_DB.items():
        summary.append({
            "event_key": key,
            "title": event["title"],
            "category": event["category"],
            "venue": event["venue"],
            "time": f"{event['start_time']} - {event['end_time']}",
            "team_size": f"{event['min_team_size']}-{event['max_team_size']} members",
            "fee": f"Rs. {event['registration_fee']}"
        })
    return summary


def get_event_details(event_name: str) -> Optional[Dict[str, Any]]:
    """
    Search and return full details and rules for a given event name or keyword.
    """
    import re
    try:
        from app.core.database import SessionLocal
        from app.models.event import Event
        db = SessionLocal()
        try:
            clean = event_name.lower().strip()
            db_events = db.query(Event).filter(Event.is_active == True).all()

            # 1. Exact or substring match of event title
            for ev in db_events:
                ev_name_lower = ev.name.lower()
                if ev_name_lower == clean or ev_name_lower in clean:
                    rules = [r.rule_text for r in ev.rules] if ev.rules else [
                        "All submissions must be original work.",
                        "Participants must follow organizer guidelines."
                    ]
                    return {
                        "id": ev.id,
                        "title": ev.name,
                        "category": ev.category.name if ev.category else "General",
                        "venue": ev.venue.name if ev.venue else "Campus",
                        "start_time": f"{ev.event_date}, {ev.start_time.strftime('%I:%M %p')}",
                        "end_time": f"{ev.event_date}, {ev.end_time.strftime('%I:%M %p')}",
                        "min_team_size": ev.min_team_size,
                        "max_team_size": ev.max_team_size,
                        "registration_fee": float(ev.registration_fee),
                        "rules": rules
                    }

            # 2. Token match excluding common query stopwords
            stopwords = {"what", "are", "the", "for", "and", "rules", "rule", "detail", "details",
                         "when", "where", "about", "show", "tell", "give", "info", "information",
                         "event", "events", "how", "much", "many", "does", "cost"}
            words = [w for w in re.findall(r'[a-zA-Z0-9]+', clean) if len(w) > 2 and w not in stopwords]
            
            best_match = None
            max_matches = 0
            for ev in db_events:
                ev_tokens = set(re.findall(r'[a-zA-Z0-9]+', ev.name.lower()))
                matches = sum(1 for w in words if w in ev_tokens or any(w in t for t in ev_tokens))
                if matches > max_matches:
                    max_matches = matches
                    best_match = ev

            if best_match and max_matches > 0:
                rules = [r.rule_text for r in best_match.rules] if best_match.rules else [
                    "All submissions must be original work.",
                    "Participants must follow organizer guidelines."
                ]
                return {
                    "id": best_match.id,
                    "title": best_match.name,
                    "category": best_match.category.name if best_match.category else "General",
                    "venue": best_match.venue.name if best_match.venue else "Campus",
                    "start_time": f"{best_match.event_date}, {best_match.start_time.strftime('%I:%M %p')}",
                    "end_time": f"{best_match.event_date}, {best_match.end_time.strftime('%I:%M %p')}",
                    "min_team_size": best_match.min_team_size,
                    "max_team_size": best_match.max_team_size,
                    "registration_fee": float(best_match.registration_fee),
                    "rules": rules
                }
        finally:
            db.close()
    except Exception:
        pass

    # Fallback search in FEST_EVENTS_DB
    clean_name = event_name.lower().replace(" ", "").replace("-", "")
    for key, event in FEST_EVENTS_DB.items():
        if key in clean_name or clean_name in key or event["title"].lower().replace(" ", "") in clean_name:
            return event
    for key, event in FEST_EVENTS_DB.items():
        if any(word in event["title"].lower() for word in event_name.lower().split()):
            return event
    return None


def check_schedule_clash(event1_name: str, event2_name: str) -> Dict[str, Any]:
    """
    Checks if two events clash in time or venue.
    """
    e1 = get_event_details(event1_name)
    e2 = get_event_details(event2_name)
    
    if not e1 or not e2:
        return {"clash": False, "reason": "One or both events could not be found."}
    
    venue_clash = (e1["venue"].lower() == e2["venue"].lower())
    time_clash = (e1["start_time"] == e2["start_time"])
    
    return {
        "event_1": e1["title"],
        "event_2": e2["title"],
        "venue_clash": venue_clash,
        "time_clash": time_clash,
        "has_conflict": venue_clash or time_clash,
        "details": f"{e1['title']} ({e1['start_time']} at {e1['venue']}) vs {e2['title']} ({e2['start_time']} at {e2['venue']})"
    }
