"""
tools/event_tools.py - Event Management and Scheduling Tools
"""

from typing import Dict, Any, List, Optional

# Sample in-memory database of fest events
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
        "venue": "Auditorium Hall",
        "start_time": "Day 1, 05:00 PM",
        "end_time": "Day 1, 09:00 PM",
        "min_team_size": 3,
        "max_team_size": 8,
        "registration_fee": 1000,
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
    clean_name = event_name.lower().replace(" ", "").replace("-", "")
    for key, event in FEST_EVENTS_DB.items():
        if key in clean_name or clean_name in key or event["title"].lower().replace(" ", "") in clean_name:
            return event
    # Partial match fallback
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
