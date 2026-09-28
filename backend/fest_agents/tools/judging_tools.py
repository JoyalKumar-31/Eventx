"""
tools/judging_tools.py - Judging, Evaluation, Scoring, and Automatic Rankings
"""

from typing import Dict, Any, List


# Standard evaluation rubrics per category
RUBRICS = {
    "Technical": {
        "Innovation & Originality": 25,
        "Technical Complexity": 25,
        "Practical Feasibility": 25,
        "Presentation & Q/A": 25
    },
    "Robotics": {
        "Design & Mechanism": 30,
        "Arena Performance & Agility": 35,
        "Robustness": 20,
        "Safety Compliance": 15
    },
    "Cultural": {
        "Artistic Expression": 30,
        "Synchronization & Rhythm": 25,
        "Stage Presence": 25,
        "Audience Impact": 20
    }
}


def get_evaluation_rubric(category: str = "Technical") -> Dict[str, Any]:
    """Returns the marking criteria and weightage for judges."""
    for key, rubric in RUBRICS.items():
        if key.lower() in category.lower():
            return {"category": key, "rubric": rubric, "max_score": 100}
    return {"category": "Technical", "rubric": RUBRICS["Technical"], "max_score": 100}


def calculate_rankings(scores_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes a list of evaluated teams with judge marks and computes ranked standings.
    Example item: {"team_name": "Team A", "scores": {"innovation": 24, "tech": 22, ...}, "remarks": "..."}
    """
    evaluated = []
    for item in scores_list:
        scores = item.get("scores", {})
        total = sum(scores.values()) if isinstance(scores, dict) else float(scores)
        evaluated.append({
            "team_name": item.get("team_name", "Unknown Team"),
            "total_score": total,
            "remarks": item.get("remarks", "No remarks provided"),
            "details": scores
        })
    
    # Sort descending by total score
    evaluated.sort(key=lambda x: x["total_score"], reverse=True)
    
    # Assign positions
    ranked = []
    positions = ["1st Place (Winner)", "2nd Place (Runner Up)", "3rd Place (2nd Runner Up)"]
    for idx, team in enumerate(evaluated):
        pos_label = positions[idx] if idx < len(positions) else f"Rank #{idx + 1}"
        team_entry = {
            "rank": idx + 1,
            "position": pos_label,
            **team
        }
        ranked.append(team_entry)
        
    return ranked


def get_live_event_results(event_name_or_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves live evaluated results or published rankings for an event from MySQL.
    """
    try:
        from app.core.database import SessionLocal
        from app.models.event import Event
        from app.models.judging import EventResult, Evaluation
        from app.models.team import Team

        db = SessionLocal()
        try:
            clean = event_name_or_id.lower().strip()
            db_events = db.query(Event).filter(Event.is_active == True).all()
            ev = None
            # 1. Exact ID
            for e in db_events:
                if str(e.id) == clean:
                    ev = e
                    break
            # 2. Name substring or keyword
            if not ev:
                for e in db_events:
                    e_name = e.name.lower()
                    if e_name in clean or any(w in clean for w in e_name.split() if len(w) > 3):
                        ev = e
                        break

            if ev:
                # 1. Check published EventResult
                results = db.query(EventResult).filter(EventResult.event_id == ev.id).order_by(EventResult.rank.asc()).all()
                if results:
                    positions = ["1st Place (Winner)", "2nd Place (Runner Up)", "3rd Place (2nd Runner Up)"]
                    ranked = []
                    for idx, r in enumerate(results):
                        pos_label = positions[idx] if idx < len(positions) else f"Rank #{r.rank}"
                        ranked.append({
                            "rank": r.rank,
                            "position": pos_label,
                            "team_name": r.team.name if r.team else f"Team #{r.team_id}",
                            "total_score": float(r.average_score),
                            "event": ev.name,
                            "is_published": r.is_published
                        })
                    return ranked

                # 2. Check live evaluations
                evals = db.query(Evaluation).filter(Evaluation.event_id == ev.id).all()
                if evals:
                    scores_list = []
                    for ev_item in evals:
                        scores_list.append({
                            "team_name": ev_item.team.name if ev_item.team else f"Team #{ev_item.team_id}",
                            "scores": {
                                "innovation": ev_item.innovation,
                                "technical_execution": ev_item.technical_execution,
                                "presentation": ev_item.presentation
                            },
                            "remarks": ev_item.remarks or "Evaluated"
                        })
                    return calculate_rankings(scores_list)
        finally:
            db.close()
    except Exception:
        pass

    return []

