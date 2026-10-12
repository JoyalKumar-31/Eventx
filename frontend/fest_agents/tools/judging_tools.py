"""
tools/judging_tools.py - Judging, Evaluation, Scoring, and Automatic Rankings
Provides comprehensive actions and queries for Judges and Evaluators on EventX.
"""

from typing import Dict, Any, List, Optional, Tuple
import re
from datetime import datetime, timezone


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


def resolve_event_for_judging(query_or_name: Optional[str] = None, judge_id: Optional[int] = None, db_session = None):
    """
    Resolves target competition from natural language query or judge's assigned panels.
    """
    try:
        from app.db.session import SessionLocal
        from app.models.event import Event
        from app.models.judging import JudgeAssignment
        from app.models.enums import EventStatus

        owns_session = False
        if db_session is None:
            s = SessionLocal()
            owns_session = True
        else:
            s = db_session

        try:
            clean = (query_or_name or "").lower().strip()

            # 1. Exact numeric ID
            if clean.isdigit():
                ev = s.query(Event).filter(Event.id == int(clean)).first()
                if ev:
                    return ev

            events = (
                s.query(Event)
                .filter(Event.status != EventStatus.DRAFT)
                .order_by(Event.created_at.desc(), Event.id.desc())
                .all()
            )

            if clean:
                # Filter noise and stop words
                cleaned_text = re.sub(
                    r'\b(who|got|the|maximum|max|highest|top|best|lowest|score|scores|marks|points|in|for|of|event|competition|contest|tell|me|calculate|give|what|is|are|winner|leading|participants|registered|teams|submissions)\b',
                    ' ',
                    clean
                )
                words = [w for w in cleaned_text.split() if len(w) >= 3]

                # Exact title match
                for e in events:
                    if e.title.lower() == clean or e.title.lower() == cleaned_text.strip():
                        return e

                # Event title substring in query
                for e in events:
                    if e.title.lower() in clean:
                        return e

                # Exact word intersection
                for e in events:
                    e_words = [w for w in e.title.lower().split() if len(w) >= 3]
                    if any(w in words for w in e_words):
                        return e

                # Partial substring in title
                for w in words:
                    for e in events:
                        if w in e.title.lower():
                            return e

            # Fallback to Judge's assignments
            if judge_id:
                assignment = s.query(JudgeAssignment).filter(JudgeAssignment.judge_id == judge_id).first()
                if assignment and assignment.event:
                    return assignment.event

            return events[0] if events else None
        finally:
            if owns_session:
                s.close()
    except Exception:
        return None


def get_live_event_results(event_name_or_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves live evaluated results or published rankings for an event from MySQL.
    """
    try:
        from app.db.session import SessionLocal
        from app.models.event import Event
        from app.models.judging import Result, Score
        from app.models.registration import Registration
        from sqlalchemy import func

        db = SessionLocal()
        try:
            ev = resolve_event_for_judging(event_name_or_id, db_session=db)
            if not ev:
                return []

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

            # 2. Check live Score tabulations strictly linked to registrations of this event
            scores = db.query(
                Score.registration_id,
                func.sum(Score.score_value).label("total")
            ).join(Registration, Score.registration_id == Registration.id)\
             .filter(Registration.event_id == ev.id)\
             .group_by(Score.registration_id)\
             .order_by(func.sum(Score.score_value).desc()).all()

            if scores:
                positions = ["1st Place (Leader)", "2nd Place (Runner-up)", "3rd Place (2nd Runner-up)"]
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


def get_event_maximum_score_and_standings(
    event_name_or_id: Optional[str] = None,
    judge_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculates who achieved the maximum score in a specific event, detailed breakdown,
    complete leaderboard standings, and pending evaluations directly from MySQL.
    """
    try:
        from app.db.session import SessionLocal
        from app.models.event import Event
        from app.models.judging import Result, Score, ScoreCriteria, JudgeAssignment
        from app.models.registration import Registration
        from app.models.user import User
        from sqlalchemy import func

        db = SessionLocal()
        try:
            ev = resolve_event_for_judging(event_name_or_id, judge_id, db_session=db)
            if not ev:
                return {
                    "success": False,
                    "event_title": "Festival Competition",
                    "has_scores": False,
                    "message": "⚠️ Could not identify the requested event. Please specify the competition name (e.g., *'Coding'*, *'Algorithm Masters Sprint'*, or *'RoboWars'*)."
                }

            # 1. Check if Results table has finalized winners
            results = db.query(Result).filter(Result.event_id == ev.id).order_by(Result.rank.asc()).all()
            if results:
                top_res = results[0]
                winner_name = top_res.registration.team.name if (top_res.registration and top_res.registration.team) else (
                    top_res.registration.user.full_name if (top_res.registration and top_res.registration.user) else f"Entry #{top_res.registration_id}"
                )
                winner_reg = top_res.registration.registration_number if top_res.registration else "N/A"
                max_score = round(float(top_res.total_score), 2)
                award = top_res.award_title or "1st Place Winner"

                standings_lines = []
                for r in results:
                    r_name = r.registration.team.name if (r.registration and r.registration.team) else (
                        r.registration.user.full_name if (r.registration and r.registration.user) else f"Entry #{r.registration_id}"
                    )
                    standings_lines.append(f"• **Rank #{r.rank} ({r.award_title or 'Place'})**: **{r_name}** — **{round(float(r.total_score), 2)} pts** (Reg ID: `{r.registration.registration_number if r.registration else 'N/A'}`)")

                msg = (
                    f"### 🏆 Official Final Results & Maximum Score: {ev.title}\n\n"
                    f"🥇 **Highest Score & Winner**: **{winner_name}**\n"
                    f"• **Registration ID**: `{winner_reg}`\n"
                    f"• **Maximum Final Score**: **{max_score} pts**\n"
                    f"• **Award Designation**: 🎖️ **{award}**\n"
                    f"• **Publication Status**: ✅ Published to Live Results\n\n"
                    f"📊 **Final Leaderboard Standings**:\n"
                    + "\n".join(standings_lines)
                    + f"\n\nOfficial verified credentials and certificates can be inspected publicly at [/results](/results)."
                )
                return {
                    "success": True,
                    "event_title": ev.title,
                    "has_scores": True,
                    "top_scorer": winner_name,
                    "max_score": max_score,
                    "message": msg
                }

            # 2. Compute dynamic live scores from MySQL
            score_rows = db.query(
                Score.registration_id,
                func.sum(Score.score_value).label('total_score'),
                func.count(Score.id).label('criteria_count')
            ).join(Registration, Score.registration_id == Registration.id)\
             .filter(Registration.event_id == ev.id)\
             .group_by(Score.registration_id)\
             .order_by(func.sum(Score.score_value).desc()).all()

            all_regs = db.query(Registration).filter(Registration.event_id == ev.id).all()
            scored_reg_ids = {row.registration_id for row in score_rows}
            pending_regs = [r for r in all_regs if r.id not in scored_reg_ids]

            if not score_rows:
                # No scores recorded yet
                reg_lines = []
                for r in all_regs[:5]:
                    p_name = r.user.full_name if r.user else "Student"
                    t_name = f" (Team: {r.team.name})" if r.team else ""
                    reg_lines.append(f"• **{p_name}**{t_name} — Reg ID: `{r.registration_number}`")
                roster_txt = "\n".join(reg_lines) if reg_lines else "• *No registered competitors found.*"

                first_student = all_regs[0].user.full_name if (all_regs and all_regs[0].user) else "competitor"
                msg = (
                    f"### ⚖️ Evaluation Status & Scoring: {ev.title}\n\n"
                    f"ℹ️ **No evaluation scores have been submitted yet** for **{ev.title}**.\n\n"
                    f"👥 **Registered Competitors Ready for Evaluation ({len(all_regs)})**:\n"
                    f"{roster_txt}\n\n"
                    f"📝 **How to Record Scores as Judge**:\n"
                    f"• Tell me: *'Score 85 for {first_student} in {ev.title}'*\n"
                    f"• Or say: *'Calculate scores for {first_student}: Problem Solving: 25, Code Quality: 24, Execution: 23'*\n"
                    f"• Or launch your live [Judge Scoring Console](/judge/scoring?event={ev.id})."
                )
                return {
                    "success": True,
                    "event_title": ev.title,
                    "has_scores": False,
                    "message": msg
                }

            # Top Scorer calculation
            top_score_val = float(score_rows[0].total_score)
            joint_leaders = [row for row in score_rows if float(row.total_score) == top_score_val]

            # Detailed breakdown for Rank 1
            top_row = score_rows[0]
            top_reg = db.query(Registration).filter(Registration.id == top_row.registration_id).first()
            top_name = top_reg.user.full_name if (top_reg and top_reg.user) else f"Competitor #{top_row.registration_id}"
            top_team = top_reg.team.name if (top_reg and top_reg.team) else None
            top_reg_num = top_reg.registration_number if top_reg else "N/A"
            max_score = round(top_score_val, 2)

            crit_scores = db.query(Score, ScoreCriteria)\
                .outerjoin(ScoreCriteria, Score.criteria_id == ScoreCriteria.id)\
                .filter(Score.registration_id == top_row.registration_id).all()

            breakdown_lines = []
            remarks_list = []
            for score_obj, crit_obj in crit_scores:
                c_name = crit_obj.name if crit_obj else "Score"
                breakdown_lines.append(f"  - **{c_name}**: `{score_obj.score_value} pts`")
                if score_obj.remarks:
                    remarks_list.append(score_obj.remarks)

            breakdown_str = "\n".join(breakdown_lines) if breakdown_lines else f"  - Total Aggregate: `{max_score} pts`"
            remarks_str = f"• **Judge Remarks**: *\"{remarks_list[0]}\"*\n" if remarks_list else ""

            # Standings table
            standings_lines = []
            medals = ["🥇 1st Place (Leader)", "🥈 2nd Place (Runner-up)", "🥉 3rd Place (2nd Runner-up)"]
            for idx, row in enumerate(score_rows):
                reg_item = db.query(Registration).filter(Registration.id == row.registration_id).first()
                p_name = reg_item.user.full_name if (reg_item and reg_item.user) else f"Competitor #{row.registration_id}"
                t_name = f" ({reg_item.team.name})" if (reg_item and reg_item.team) else ""
                pos = medals[idx] if idx < len(medals) else f"Rank #{idx + 1}"
                standings_lines.append(f"• **{pos}**: **{p_name}**{t_name} — Score: **{round(float(row.total_score), 2)} pts** (Reg ID: `{reg_item.registration_number if reg_item else 'N/A'}`)")

            standings_str = "\n".join(standings_lines)

            # Pending participants
            pending_lines = []
            for r in pending_regs[:5]:
                p_name = r.user.full_name if r.user else "Competitor"
                pending_lines.append(f"• **{p_name}** (`{r.registration_number}`) — *Pending Evaluation*")
            pending_str = ("\n\n⏳ **Pending Evaluation (" + str(len(pending_regs)) + ")**:\n" + "\n".join(pending_lines)) if pending_lines else "\n\n✅ *All registered competitors have been evaluated!*"

            # Header for joint leaders vs single leader
            if len(joint_leaders) > 1:
                leader_names = ", ".join(
                    f"**{(db.query(Registration).filter(Registration.id == r.registration_id).first().user.full_name if db.query(Registration).filter(Registration.id == r.registration_id).first().user else 'Competitor')}**"
                    for r in joint_leaders
                )
                leader_header = f"🥇 **Joint Leaders (Maximum Score: {max_score} pts)**: {leader_names}\n"
            else:
                leader_header = f"🥇 **Top Scorer (Maximum Score)**: **{top_name}**" + (f" ({top_team})" if top_team else "") + f"\n• **Registration ID**: `{top_reg_num}`\n• **Maximum Score**: **{max_score} pts**\n"

            message = (
                f"### 🏆 Maximum Score & Leaderboard: {ev.title}\n\n"
                f"{leader_header}"
                f"• **Criteria Breakdown**:\n{breakdown_str}\n"
                f"{remarks_str}\n"
                f"📊 **Current Leaderboard Standings**:\n"
                f"{standings_str}"
                f"{pending_str}\n\n"
                f"💡 *To evaluate any pending competitor or adjust marks, say: 'Score [marks] for [Name] in {ev.title}' or open the [Judge Scoring Console](/judge/scoring?event={ev.id}).*"
            )

            return {
                "success": True,
                "event_title": ev.title,
                "has_scores": True,
                "top_scorer": top_name,
                "max_score": max_score,
                "message": message
            }
        finally:
            db.close()
    except Exception as exc:
        return {
            "success": False,
            "message": f"Could not calculate maximum score due to error: {str(exc)}"
        }


def get_event_participants_for_judging(
    event_name_or_id: Optional[str] = None,
    judge_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Returns the list of competitors and teams registered for an event with evaluation status.
    """
    try:
        from app.db.session import SessionLocal
        from app.models.event import Event
        from app.models.registration import Registration
        from app.models.judging import Score
        from sqlalchemy import func

        db = SessionLocal()
        try:
            ev = resolve_event_for_judging(event_name_or_id, judge_id, db_session=db)
            if not ev:
                return {"success": False, "message": "Could not identify the requested event."}

            from app.models.attendance import Attendance
            from app.models.enums import AttendanceStatus, RegistrationStatus

            regs = db.query(Registration).filter(Registration.event_id == ev.id).all()
            items = []
            evaluated_count = 0
            checked_in_count = 0

            for r in regs:
                p_name = r.user.full_name if r.user else "Student"
                t_name = f" ({r.team.name})" if r.team else ""

                is_checked_in = (
                    r.status == RegistrationStatus.ATTENDED
                    or db.query(Attendance).filter(
                        Attendance.registration_id == r.id,
                        Attendance.event_id == ev.id,
                        Attendance.entry_status == AttendanceStatus.VALID
                    ).first() is not None
                )
                if is_checked_in:
                    checked_in_count += 1
                    gate_badge = "🎫 **Gate Approved**"
                else:
                    gate_badge = "⏳ **Gate Check-In Pending**"

                score_sum = db.query(func.sum(Score.score_value)).filter(Score.registration_id == r.id).scalar()
                if score_sum is not None:
                    evaluated_count += 1
                    status_txt = f"✅ **Evaluated** (Score: `{round(float(score_sum), 2)} pts`)"
                else:
                    if is_checked_in:
                        status_txt = "⏳ **Awaiting Scorecard**"
                    else:
                        status_txt = "🚫 **Locked (Requires Gate QR Scan)**"

                items.append(f"• **{p_name}**{t_name} | Reg: `{r.registration_number}` | Gate: {gate_badge} | Scoring: {status_txt}")

            roster_txt = "\n".join(items) if items else "• *No registered competitors found.*"
            msg = (
                f"### 📋 Competitor Roster for {ev.title}\n\n"
                f"• **Total Registered**: {len(regs)} | **Gate Checked-In**: {checked_in_count} | **Evaluated**: {evaluated_count} | **Pending**: {len(regs) - evaluated_count}\n\n"
                f"{roster_txt}\n\n"
                f"To submit marks, say: *'Score [marks] for [Name] in {ev.title}'* or open [Judge Scoring Console](/judge/scoring?event={ev.id})."
            )
            return {"success": True, "event_title": ev.title, "message": msg}
        finally:
            db.close()
    except Exception as exc:
        return {"success": False, "message": f"Error fetching participants: {str(exc)}"}


def get_participant_scorecard(
    participant_or_reg: str,
    event_name_or_id: Optional[str] = None,
    judge_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Retrieves full evaluation scorecard for a competitor or registration number.
    """
    try:
        from app.db.session import SessionLocal
        from app.models.registration import Registration
        from app.models.judging import Score, ScoreCriteria, JudgeAssignment
        from app.models.user import User

        db = SessionLocal()
        try:
            ev = resolve_event_for_judging(event_name_or_id, judge_id, db_session=db) if event_name_or_id else None

            clean_target = participant_or_reg.lower().strip()
            query = db.query(Registration)
            if ev:
                query = query.filter(Registration.event_id == ev.id)

            regs = query.all()
            matched_reg = None
            for r in regs:
                if clean_target in r.registration_number.lower():
                    matched_reg = r
                    break
                if r.user and clean_target in r.user.full_name.lower():
                    matched_reg = r
                    break

            if not matched_reg:
                return {"success": False, "message": f"Could not find competitor or registration `{participant_or_reg}`."}

            scores = db.query(Score, ScoreCriteria, User)\
                .outerjoin(ScoreCriteria, Score.criteria_id == ScoreCriteria.id)\
                .outerjoin(JudgeAssignment, Score.judge_assignment_id == JudgeAssignment.id)\
                .outerjoin(User, JudgeAssignment.judge_id == User.id)\
                .filter(Score.registration_id == matched_reg.id).all()

            if not scores:
                return {
                    "success": True,
                    "message": f"ℹ️ **{matched_reg.user.full_name if matched_reg.user else matched_reg.registration_number}** has not received any evaluation scores yet for **{matched_reg.event.title}**."
                }

            total = sum(s_obj.score_value for s_obj, _, _ in scores)
            lines = [
                f"• **{c.name if c else 'Criteria'}**: `{s_obj.score_value} pts`" + (f" (*{s_obj.remarks}*)" if s_obj.remarks else "")
                for s_obj, c, _ in scores
            ]

            msg = (
                f"### ⚖️ Scorecard: {matched_reg.user.full_name if matched_reg.user else 'Competitor'}\n\n"
                f"• **Event**: {matched_reg.event.title}\n"
                f"• **Registration ID**: `{matched_reg.registration_number}`\n"
                f"• **Total Aggregate Score**: **{round(float(total), 2)} pts**\n\n"
                f"**Detailed Marks Breakdown**:\n"
                + "\n".join(lines)
            )
            return {"success": True, "message": msg}
        finally:
            db.close()
    except Exception as exc:
        return {"success": False, "message": f"Error fetching scorecard: {str(exc)}"}


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
            matched_event = resolve_event_for_judging(event_name_or_id, judge_id, db_session=db)
            if not matched_event:
                db_events = (
                    db.query(Event)
                    .filter(Event.status != EventStatus.DRAFT)
                    .order_by(Event.created_at.desc(), Event.id.desc())
                    .all()
                )
                matched_event = db_events[0] if db_events else None

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
            effective_judge_id = judge_id or 7 # fallback to primary judge
            if matched_reg and matched_event:
                # Enforce gate attendance check
                from app.models.attendance import Attendance
                from app.models.enums import AttendanceStatus, RegistrationStatus
                has_attended = (
                    matched_reg.status == RegistrationStatus.ATTENDED
                    or db.query(Attendance).filter(
                        Attendance.registration_id == matched_reg.id,
                        Attendance.event_id == matched_event.id,
                        Attendance.entry_status == AttendanceStatus.VALID
                    ).first() is not None
                )
                if not has_attended:
                    return {
                        "success": False,
                        "event_title": event_title,
                        "team_name": team_label,
                        "message": (
                            f"⚠️ **Gate Attendance Approval Required**: Cannot submit official scores for **{team_label}**.\n\n"
                            f"Participant has not been checked in at the event gate yet. "
                            f"Their entry ticket QR code must be scanned and approved by the coordinator before judging scorecards can be recorded."
                        )
                    }

                assignment = db.query(JudgeAssignment).filter(
                    JudgeAssignment.event_id == matched_event.id,
                    JudgeAssignment.judge_id == effective_judge_id
                ).first()

                if not assignment:
                    assignment = JudgeAssignment(
                        event_id=matched_event.id,
                        judge_id=effective_judge_id,
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
                        user_id=effective_judge_id,
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
            "remarks": remarks or f"Calculated (offline): {str(exc)}"
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


def get_event_criteria_and_rubrics(event_name_or_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves the scoring criteria and rubrics configured in MySQL for an event.
    """
    try:
        from app.db.session import SessionLocal
        from app.models.judging import ScoreCriteria

        db = SessionLocal()
        try:
            ev = resolve_event_for_judging(event_name_or_id, db_session=db)
            if not ev:
                rubric_data = get_evaluation_rubric("Technical")
                return {
                    "success": True,
                    "event_title": "General Competition",
                    "rubric": rubric_data["rubric"],
                    "max_score": 100
                }

            criteria_list = db.query(ScoreCriteria).filter(ScoreCriteria.event_id == ev.id).all()
            if criteria_list:
                crit_dict = {c.name: c.max_score for c in criteria_list}
                return {
                    "success": True,
                    "event_title": ev.title,
                    "rubric": crit_dict,
                    "max_score": sum(c.max_score for c in criteria_list),
                    "items": [
                        {"name": c.name, "max_score": c.max_score, "weightage": c.weightage, "description": c.description}
                        for c in criteria_list
                    ]
                }

            cat_name = ev.category.name if ev.category else "Technical"
            rubric_data = get_evaluation_rubric(cat_name)
            return {
                "success": True,
                "event_title": ev.title,
                "rubric": rubric_data["rubric"],
                "max_score": 100
            }
        finally:
            db.close()
    except Exception:
        rubric_data = get_evaluation_rubric("Technical")
        return {
            "success": True,
            "event_title": event_name_or_id or "General",
            "rubric": rubric_data["rubric"],
            "max_score": 100
        }


def add_event_scoring_criteria(
    event_name_or_id: str,
    criteria_name: str,
    max_score: float = 25.0,
    weightage: float = 1.0,
    description: Optional[str] = None,
    judge_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Creates a new evaluation criteria for an event in MySQL.
    """
    try:
        from app.db.session import SessionLocal
        from app.models.judging import ScoreCriteria

        db = SessionLocal()
        try:
            ev = resolve_event_for_judging(event_name_or_id, judge_id, db_session=db)
            if not ev:
                return {"success": False, "message": "Event not found."}

            crit = ScoreCriteria(
                event_id=ev.id,
                name=criteria_name.strip(),
                max_score=float(max_score),
                weightage=float(weightage),
                description=description
            )
            db.add(crit)
            db.commit()
            db.refresh(crit)

            return {
                "success": True,
                "message": (
                    f"✅ **Criteria Added Successfully to {ev.title}**!\n\n"
                    f"• **Criterion**: **{crit.name}**\n"
                    f"• **Max Score**: `{crit.max_score} pts`\n"
                    f"• **Weightage**: `{crit.weightage}`\n\n"
                    f"You can now score participants against this rubric."
                )
            }
        finally:
            db.close()
    except Exception as exc:
        return {"success": False, "message": f"Could not add criteria: {str(exc)}"}


def publish_or_finalize_event_results(
    event_name_or_id: str,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Finalizes scores, generates Result records, and publishes winners to MySQL.
    """
    try:
        from app.db.session import SessionLocal
        from app.services.judging_service import publish_event_results

        db = SessionLocal()
        try:
            ev = resolve_event_for_judging(event_name_or_id, user_id, db_session=db)
            if not ev:
                return {"success": False, "message": "Event not found."}

            effective_publisher_id = user_id or 1
            results = publish_event_results(
                db=db,
                event_id=ev.id,
                published_by_user_id=effective_publisher_id
            )

            lines = []
            for r in results:
                name = r.registration.user.full_name if (r.registration and r.registration.user) else f"Reg #{r.registration_id}"
                lines.append(f"• **Rank #{r.rank} ({r.award_title or 'Place'})**: **{name}** — **{r.total_score} pts**")

            return {
                "success": True,
                "message": (
                    f"🏆 **Results Finalized & Published for {ev.title}**!\n\n"
                    + "\n".join(lines)
                    + f"\n\nResults are now live and visible to all participants at [/results](/results)."
                )
            }
        finally:
            db.close()
    except Exception as exc:
        return {"success": False, "message": f"Could not publish results: {str(exc)}"}
