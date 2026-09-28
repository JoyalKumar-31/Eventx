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
