from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.judging import JudgeAssignment, ScoreCriteria, Score, Result
from app.models.event import Event
from app.models.registration import Registration
from app.models.attendance import Attendance
from app.models.user import User
from app.models.enums import JudgeAssignmentStatus, UserRole, EventStatus, NotificationType, RegistrationStatus, AttendanceStatus
from app.schemas.judging import ScoreSubmissionRequest
from app.services.audit_service import log_action
from app.services.notification_service import create_notification
from app.services.certificate_service import issue_certificate_for_registration


def assign_judge_to_event(
    db: Session,
    event_id: int,
    judge_id: int,
    round_id: Optional[int] = None
) -> JudgeAssignment:
    # Verify user is a judge
    judge = db.query(User).filter(User.id == judge_id).first()
    if not judge or judge.role != UserRole.JUDGE:
        raise HTTPException(status_code=400, detail="Specified user does not have the JUDGE role")

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    existing = db.query(JudgeAssignment).filter(
        JudgeAssignment.event_id == event_id,
        JudgeAssignment.judge_id == judge_id,
        JudgeAssignment.round_id == round_id
    ).first()
    if existing:
        return existing

    assignment = JudgeAssignment(
        event_id=event_id,
        judge_id=judge_id,
        round_id=round_id,
        status=JudgeAssignmentStatus.ASSIGNED
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    create_notification(
        db,
        user_id=judge_id,
        title="Event Judging Assignment",
        message=f"You have been assigned to judge the event '{event.title}'.",
        link=f"/judge/scoring?event={event_id}"
    )

    return assignment


def submit_scores(
    db: Session,
    judge_user_id: int,
    event_id: int,
    submission: ScoreSubmissionRequest
) -> List[Score]:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    user = db.query(User).filter(User.id == judge_user_id).first()

    # Verify event status & event day commencement
    if event.status in [EventStatus.DRAFT, EventStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit scores for an event with status '{event.status.value}'. The event must be opened."
        )

    if event.status == EventStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This event is already completed and results have been finalized. Scoring is closed."
        )

    # Verify judge is assigned to this event OR is the event coordinator/admin
    assignment = db.query(JudgeAssignment).filter(
        JudgeAssignment.event_id == event_id,
        JudgeAssignment.judge_id == judge_user_id
    ).first()

    if not assignment:
        # If user is the event coordinator or admin, create/link an assignment for their evaluation
        if (user and user.role == UserRole.ADMIN) or (event.coordinator_id == judge_user_id):
            assignment = JudgeAssignment(
                event_id=event_id,
                judge_id=judge_user_id,
                status=JudgeAssignmentStatus.ASSIGNED
            )
            db.add(assignment)
            db.flush()
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned as an authorized judge for this event."
            )

    # Verify registration belongs to event
    registration = db.query(Registration).filter(
        Registration.id == submission.registration_id,
        Registration.event_id == event_id
    ).first()
    if not registration:
        raise HTTPException(status_code=400, detail="Participant registration does not match this event")

    # Verify participant has gate attendance approval via QR scan
    has_valid_attendance = (
        registration.status == RegistrationStatus.ATTENDED
        or db.query(Attendance).filter(
            Attendance.registration_id == registration.id,
            Attendance.event_id == event_id,
            Attendance.entry_status == AttendanceStatus.VALID
        ).first() is not None
    )

    if not has_valid_attendance:
        participant_name = (
            registration.team.name
            if registration.team
            else (registration.user.full_name if registration.user else f"Participant #{registration.id}")
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Gate check-in required! Cannot submit scores for {participant_name} "
                f"because their attendance has not been approved via QR code scanning at the entrance yet."
            )
        )

    saved_scores = []
    for entry in submission.scores:
        criteria = db.query(ScoreCriteria).filter(ScoreCriteria.id == entry.criteria_id).first()
        if not criteria or criteria.event_id != event_id:
            raise HTTPException(status_code=400, detail=f"Criteria ID {entry.criteria_id} not valid for this event")

        if entry.score_value < 0 or entry.score_value > criteria.max_score:
            raise HTTPException(
                status_code=400,
                detail=f"Score {entry.score_value} exceeds maximum allowed score of {criteria.max_score} for {criteria.name}"
            )

        # Disallow re-scoring once score has been submitted
        existing_score = db.query(Score).filter(
            Score.judge_assignment_id == assignment.id,
            Score.criteria_id == criteria.id,
            Score.registration_id == submission.registration_id
        ).first()

        if existing_score:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Score has already been submitted and finalized for this competitor. You cannot submit or modify scores once submitted."
            )

        new_score = Score(
            judge_assignment_id=assignment.id,
            criteria_id=criteria.id,
            registration_id=submission.registration_id,
            score_value=entry.score_value,
            remarks=entry.remarks
        )
        db.add(new_score)
        saved_scores.append(new_score)

    db.commit()

    # Calculate total score and participant details
    total_score = sum(entry.score_value for entry in submission.scores)
    participant_name = (
        registration.team.name
        if registration.team
        else (registration.user.full_name if registration.user else f"Participant #{registration.id}")
    )
    judge_name = user.full_name if user else f"Judge #{judge_user_id}"

    # Notify event coordinator
    if event.coordinator_id:
        create_notification(
            db=db,
            user_id=event.coordinator_id,
            title="Judge Scorecard Submitted",
            message=f"Judge {judge_name} submitted official scores for {participant_name} ({total_score:.1f} pts) in '{event.title}'.",
            type=NotificationType.SUCCESS,
            link=f"/coordinator/results?event_id={event_id}"
        )

    log_action(
        db,
        action="SCORES_SUBMITTED",
        entity_type="Score",
        entity_id=str(submission.registration_id),
        user_id=judge_user_id,
        new_values={
            "event_id": event_id,
            "registration_id": submission.registration_id,
            "total_score": total_score,
            "score_count": len(submission.scores),
            "coordinator_notified": bool(event.coordinator_id)
        }
    )

    return saved_scores


def calculate_event_leaderboard(db: Session, event_id: int, round_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Compute aggregate rankings based on normalized scoring."""
    scores_query = db.query(
        Score.registration_id,
        func.sum(Score.score_value).label("total_score")
    ).join(JudgeAssignment, Score.judge_assignment_id == JudgeAssignment.id)\
     .filter(JudgeAssignment.event_id == event_id)

    if round_id:
        scores_query = scores_query.filter(JudgeAssignment.round_id == round_id)

    grouped = scores_query.group_by(Score.registration_id).order_by(func.sum(Score.score_value).desc()).all()

    leaderboard = []
    for rank, (reg_id, total) in enumerate(grouped, start=1):
        reg = db.query(Registration).filter(Registration.id == reg_id).first()
        if reg:
            reg_scores = db.query(Score).join(JudgeAssignment, Score.judge_assignment_id == JudgeAssignment.id)\
                           .filter(JudgeAssignment.event_id == event_id, Score.registration_id == reg_id).all()
            criteria_breakdown = {}
            judge_names = set()
            remarks_list = []
            for s in reg_scores:
                c_name = s.criteria.name if s.criteria else f"Criteria #{s.criteria_id}"
                criteria_breakdown[c_name] = round(float(s.score_value), 2)
                if s.judge_assignment and s.judge_assignment.judge:
                    judge_names.add(s.judge_assignment.judge.full_name)
                if s.remarks and s.remarks.strip():
                    remarks_list.append(s.remarks.strip())

            leaderboard.append({
                "registration_id": reg.id,
                "registration_number": reg.registration_number,
                "participant_name": reg.user.full_name,
                "participant_email": reg.user.email,
                "team_name": reg.team.name if reg.team else None,
                "total_score": round(float(total), 2),
                "rank": rank,
                "scores_by_criteria": criteria_breakdown,
                "judges": list(judge_names),
                "remarks": " | ".join(remarks_list) if remarks_list else None
            })
    return leaderboard


def publish_event_results(
    db: Session,
    event_id: int,
    published_by_user_id: int,
    round_id: Optional[int] = None,
    awards_map: Optional[Dict[int, str]] = None
) -> List[Result]:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    leaderboard = calculate_event_leaderboard(db, event_id, round_id)
    if not leaderboard:
        raise HTTPException(status_code=400, detail="Cannot publish results: No scores have been submitted yet.")

    # Mark the event as COMPLETED when results are submitted/published
    event.status = EventStatus.COMPLETED

    results_created = []
    now = datetime.now(timezone.utc)

    for item in leaderboard:
        reg_id = item["registration_id"]
        rank = item["rank"]
        total_score = item["total_score"]

        # Default award titles for top ranks
        award_title = None
        if awards_map and reg_id in awards_map:
            award_title = awards_map[reg_id]
        elif rank == 1:
            award_title = "1st Place Winner"
        elif rank == 2:
            award_title = "1st Runner Up"
        elif rank == 3:
            award_title = "2nd Runner Up"
        else:
            award_title = "Certificate of Participation"

        existing_res = db.query(Result).filter(
            Result.event_id == event_id,
            Result.registration_id == reg_id,
            Result.round_id == round_id
        ).first()

        if existing_res:
            existing_res.rank = rank
            existing_res.total_score = total_score
            existing_res.award_title = award_title
            existing_res.is_published = True
            existing_res.published_at = now
            existing_res.published_by_user_id = published_by_user_id
            results_created.append(existing_res)
        else:
            new_res = Result(
                event_id=event_id,
                round_id=round_id,
                registration_id=reg_id,
                rank=rank,
                total_score=total_score,
                award_title=award_title,
                is_published=True,
                published_at=now,
                published_by_user_id=published_by_user_id
            )
            db.add(new_res)
            results_created.append(new_res)

        # Issue certificate automatically
        issue_certificate_for_registration(db, reg_id, award_title=award_title)

        # Notify participant
        reg = db.query(Registration).filter(Registration.id == reg_id).first()
        if reg:
            create_notification(
                db,
                user_id=reg.user_id,
                title="Results Published!",
                message=f"Results for '{event.title}' are published. Rank: {rank}. Your certificate is now available.",
                link="/student/certificates"
            )

    db.commit()

    log_action(
        db,
        action="RESULTS_PUBLISHED",
        entity_type="Result",
        entity_id=str(event_id),
        user_id=published_by_user_id,
        new_values={"event_id": event_id, "total_ranked": len(results_created)}
    )

    return results_created
