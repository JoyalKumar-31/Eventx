from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.enums import UserRole
from app.models.judging import Score, JudgeAssignment
from app.models.user import User
from app.schemas.judging import ScoreSubmissionRequest, ScoreResponse
from app.services.judging_service import submit_scores

router = APIRouter(prefix="/scores", tags=["Judging"])


@router.post("/event/{event_id}", response_model=List[ScoreResponse], status_code=status.HTTP_200_OK)
def submit_participant_scores(
    event_id: int,
    submission: ScoreSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.JUDGE, UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    """
    Judges submit/update score per criteria with validation and remarks.
    """
    saved_scores = submit_scores(
        db=db,
        judge_user_id=current_user.id,
        event_id=event_id,
        submission=submission
    )

    return [
        ScoreResponse(
            id=s.id,
            judge_assignment_id=s.judge_assignment_id,
            criteria_id=s.criteria_id,
            criteria_name=s.criteria.name,
            registration_id=s.registration_id,
            score_value=s.score_value,
            remarks=s.remarks,
            submitted_at=s.submitted_at
        )
        for s in saved_scores
    ]


@router.get("/event/{event_id}", response_model=List[ScoreResponse])
def get_event_scores(
    event_id: int,
    registration_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.JUDGE, UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    query = db.query(Score).join(JudgeAssignment, Score.judge_assignment_id == JudgeAssignment.id)\
              .filter(JudgeAssignment.event_id == event_id, Score.registration_id == registration_id)

    # If Judge, show only their own scores
    if current_user.role == UserRole.JUDGE:
        query = query.filter(JudgeAssignment.judge_id == current_user.id)

    scores = query.all()
    return [
        ScoreResponse(
            id=s.id,
            judge_assignment_id=s.judge_assignment_id,
            criteria_id=s.criteria_id,
            criteria_name=s.criteria.name,
            registration_id=s.registration_id,
            score_value=s.score_value,
            remarks=s.remarks,
            submitted_at=s.submitted_at
        )
        for s in scores
    ]
