"""
tools/judging_tools.py - Judging, Evaluation, Scoring, and Automatic Rankings
"""

from typing import Dict, Any, List, Optional


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
        from app.db.session import SessionLocal
        from app.models.event import Event
        from app.models.judging import Result, Score
        from app.models.enums import EventStatus
        from sqlalchemy import func

        db = SessionLocal()
        try:
            clean = event_name_or_id.lower().strip()
            db_events = db.query(Event).filter(Event.status != EventStatus.DRAFT).all()
            ev = None
            # 1. Exact ID
            for e in db_events:
                if str(e.id) == clean:
                    ev = e
                    break
            # 2. Name substring or keyword
            if not ev:
                for e in db_events:
                    e_name = e.title.lower()
                    if clean in e_name or e_name in clean or any(w in clean for w in e_name.split() if len(w) > 3):
                        ev = e
                        break

            if ev:
                # 1. Check published Result records
                results = db.query(Result).filter(Result.event_id == ev.id).order_by(Result.rank.asc()).all()
                if results:
                    positions = ["1st Place (Winner)", "2nd Place (Runner Up)", "3rd Place (2nd Runner Up)"]
                    ranked = []
                    for idx, r in enumerate(results):
                        pos_label = r.award_title or (positions[idx] if idx < len(positions) else f"Rank #{r.rank}")
                        team_or_user = r.registration.team.name if (r.registration and r.registration.team) else (
                            r.registration.user.full_name if (r.registration and r.registration.user) else f"Entry #{r.registration_id}"
                        )
                        ranked.append({
                            "rank": r.rank,
                            "position": pos_label,
                            "team_name": team_or_user,
                            "total_score": float(r.total_score),
                            "event": ev.title,
                            "is_published": r.is_published
                        })
                    return ranked

                # 2. Check live Score tabulations
                scores = db.query(
                    Score.registration_id,
                    func.sum(Score.score_value).label("total")
                ).join(Score.judge_assignment).filter(
                    Score.judge_assignment.has(event_id=ev.id)
                ).group_by(Score.registration_id).order_by(func.sum(Score.score_value).desc()).all()

                if scores:
                    from app.models.registration import Registration
                    positions = ["1st Place (Leader)", "2nd Place", "3rd Place"]
                    ranked = []
                    for idx, (reg_id, total) in enumerate(scores):
                        reg = db.query(Registration).filter(Registration.id == reg_id).first()
                        team_or_user = reg.team.name if (reg and reg.team) else (reg.user.full_name if (reg and reg.user) else f"Competitor #{reg_id}")
                        pos_label = positions[idx] if idx < len(positions) else f"Rank #{idx + 1}"
                        ranked.append({
                            "rank": idx + 1,
                            "position": pos_label,
                            "team_name": team_or_user,
                            "total_score": round(float(total), 2),
                            "event": ev.title,
                            "is_published": False
                        })
                    return ranked
        finally:
            db.close()
    except Exception:
        pass

    return []


def calculate_and_record_scores(
    event_name_or_id: str,
    team_or_reg_identifier: str,
    scores_dict: Dict[str, float],
    judge_id: Optional[int] = None,
    remarks: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculates marks, criteria totals, and percentages, and persists the evaluation into MySQL.
    Computes real-time rankings and leaderboard positions.
    """
    from datetime import datetime, timezone
    try:
        from app.db.session import SessionLocal
        from app.models.event import Event
        from app.models.registration import Registration
        from app.models.judging import JudgeAssignment, ScoreCriteria, Score
        from app.models.enums import EventStatus, JudgeAssignmentStatus
        from app.services.audit_service import log_action

        db = SessionLocal()
        try:
            # 1. Resolve Event
            clean_ev = str(event_name_or_id).strip().lower()
            db_events = db.query(Event).filter(Event.status != EventStatus.DRAFT).all()
            matched_event = None

            if clean_ev.isdigit():
                matched_event = db.query(Event).filter(Event.id == int(clean_ev)).first()

            if not matched_event:
                for e in db_events:
                    e_name = e.title.lower()
                    if clean_ev == e_name or clean_ev in e_name or e_name in clean_ev:
                        matched_event = e
                        break

            if not matched_event:
                words = [w for w in clean_ev.split() if len(w) > 3]
                for e in db_events:
                    if any(w in e.title.lower() for w in words):
                        matched_event = e
                        break

            if not matched_event and db_events:
                matched_event = db_events[0]

            event_id = matched_event.id if matched_event else 1
            event_title = matched_event.title if matched_event else "Fest Competition"

            # 2. Resolve Registration / Team
            clean_target = str(team_or_reg_identifier).strip().lower()
            matched_reg = None

            if matched_event:
                regs = db.query(Registration).filter(Registration.event_id == matched_event.id).all()
                for r in regs:
                    r_num = r.registration_number.lower()
                    t_name = r.team.name.lower() if r.team else ""
                    u_name = r.user.full_name.lower() if r.user else ""
                    if clean_target in r_num or (t_name and clean_target in t_name) or (u_name and clean_target in u_name):
                        matched_reg = r
                        break
                if not matched_reg and regs:
                    matched_reg = regs[0]

            team_label = (
                matched_reg.team.name if (matched_reg and matched_reg.team) else (
                    matched_reg.user.full_name if (matched_reg and matched_reg.user) else team_or_reg_identifier
                )
            )

            # 3. Calculate Scores & Weights
            breakdown = []
            total_score = 0.0
            max_total = 0.0

            for crit_name, score_val in scores_dict.items():
                val = float(score_val)
                total_score += val
                # Default max is 25 per criteria or 100 if only 1 criteria
                max_pts = 100.0 if len(scores_dict) == 1 else (25.0 if val <= 25.0 else 50.0)
                max_total += max_pts
                breakdown.append({
                    "criteria": crit_name,
                    "score": val,
                    "max": max_pts
                })

            percentage = round((total_score / max_total) * 100, 2) if max_total > 0 else 0.0

            # 4. Save into Database if Judge Assignment is present / resolvable
            saved_to_db = False
            if judge_id and matched_reg and matched_event:
                assignment = db.query(JudgeAssignment).filter(
                    JudgeAssignment.event_id == matched_event.id,
                    JudgeAssignment.judge_id == judge_id
                ).first()

                if not assignment:
                    assignment = JudgeAssignment(
                        event_id=matched_event.id,
                        judge_id=judge_id,
                        status=JudgeAssignmentStatus.ASSIGNED
                    )
                    db.add(assignment)
                    db.flush()

                for item in breakdown:
                    crit = db.query(ScoreCriteria).filter(
                        ScoreCriteria.event_id == matched_event.id,
                        ScoreCriteria.name.ilike(item["criteria"])
                    ).first()

                    if not crit:
                        crit = ScoreCriteria(
                            event_id=matched_event.id,
                            name=item["criteria"],
                            max_score=item["max"],
                            weightage=1.0
                        )
                        db.add(crit)
                        db.flush()

                    existing_score = db.query(Score).filter(
                        Score.judge_assignment_id == assignment.id,
                        Score.criteria_id == crit.id,
                        Score.registration_id == matched_reg.id
                    ).first()

                    if existing_score:
                        existing_score.score_value = item["score"]
                        existing_score.remarks = remarks
                        existing_score.submitted_at = datetime.now(timezone.utc)
                    else:
                        new_s = Score(
                            judge_assignment_id=assignment.id,
                            criteria_id=crit.id,
                            registration_id=matched_reg.id,
                            score_value=item["score"],
                            remarks=remarks
                        )
                        db.add(new_s)

                db.commit()
                saved_to_db = True

                try:
                    log_action(
                        db,
                        action="AI_AGENT_SCORE_SUBMISSION",
                        entity_type="Score",
                        entity_id=str(matched_reg.id),
                        user_id=judge_id,
                        new_values={"event": matched_event.title, "total_score": total_score}
                    )
                except Exception:
                    pass

            # 5. Fetch updated rank
            live_rankings = get_live_event_results(str(event_id))
            current_rank = 1
            if live_rankings:
                for idx, r in enumerate(live_rankings):
                    if team_label.lower() in r["team_name"].lower():
                        current_rank = idx + 1
                        break

            return {
                "success": True,
                "event_title": event_title,
                "team_name": team_label,
                "registration_id": matched_reg.registration_number if matched_reg else "N/A",
                "breakdown": breakdown,
                "total_score": round(total_score, 2),
                "max_score": round(max_total, 2),
                "percentage": percentage,
                "current_rank": current_rank,
                "saved_to_db": saved_to_db,
                "remarks": remarks or "Evaluated via Fest AI Judge Copilot"
            }
        finally:
            db.close()
    except Exception as exc:
        # Fallback local calculation
        total = sum(float(v) for v in scores_dict.values())
        max_p = len(scores_dict) * 25.0
        return {
            "success": True,
            "event_title": event_name_or_id,
            "team_name": team_or_reg_identifier,
            "registration_id": "N/A",
            "breakdown": [{"criteria": k, "score": float(v), "max": 25.0} for k, v in scores_dict.items()],
            "total_score": total,
            "max_score": max_p,
            "percentage": round((total / max_p) * 100, 2) if max_p > 0 else 0.0,
            "current_rank": 1,
            "saved_to_db": False,
            "remarks": remarks or "Calculated via offline algorithm."
        }


def get_judge_assigned_events(judge_id: int) -> List[Dict[str, Any]]:
    """
    Returns the list of fest events assigned to this judge from MySQL.
    """
    try:
        from app.db.session import SessionLocal
        from app.models.judging import JudgeAssignment, Score
        from app.models.registration import Registration

        db = SessionLocal()
        try:
            assignments = db.query(JudgeAssignment).filter(JudgeAssignment.judge_id == judge_id).all()
            output = []
            for a in assignments:
                ev = a.event
                if not ev:
                    continue
                start_str = ev.start_time.strftime("%d %b, %I:%M %p") if ev.start_time else "TBA"
                venue_str = ev.venue.name if ev.venue else "Campus Arena"
                total_teams = db.query(Registration).filter(Registration.event_id == ev.id).count()
                evaluated_teams = db.query(Score.registration_id).filter(
                    Score.judge_assignment_id == a.id
                ).distinct().count()

                output.append({
                    "event_id": ev.id,
                    "title": ev.title,
                    "category": ev.category.name if ev.category else "General",
                    "venue": venue_str,
                    "time": start_str,
                    "total_submissions": total_teams,
                    "evaluated_submissions": evaluated_teams,
                    "pending_submissions": max(0, total_teams - evaluated_teams)
                })
            return output
        finally:
            db.close()
    except Exception:
        return []


