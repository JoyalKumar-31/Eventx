from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.enums import UserRole, JudgeAssignmentStatus
from app.models.event import Event
from app.models.judging import JudgeAssignment, ScoreCriteria
from app.models.user import User
from app.schemas.judging import (
    JudgeAssignmentCreate,
    JudgeAssignmentResponse,
    ScoreCriteriaCreate,
    ScoreCriteriaResponse
)
from app.schemas.event import EventListResponse
from app.api.v1.events import format_event_response
from app.services.judging_service import assign_judge_to_event

router = APIRouter(prefix="/judges", tags=["Judging"])


@router.post("/assign", response_model=JudgeAssignmentResponse, status_code=status.HTTP_201_CREATED)
def assign_judge(
    req: JudgeAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    assignment = assign_judge_to_event(
        db=db,
        event_id=req.event_id,
        judge_id=req.judge_id,
        round_id=req.round_id
    )
    return JudgeAssignmentResponse(
        id=assignment.id,
        event_id=assignment.event_id,
        event_title=assignment.event.title,
        judge_id=assignment.judge_id,
        judge_name=assignment.judge.full_name,
        round_id=assignment.round_id,
        round_name=assignment.round.name if assignment.round else None,
        status=assignment.status,
        assigned_at=assignment.assigned_at
    )


@router.get("/my-events", response_model=List[EventListResponse])
def get_judge_assigned_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.JUDGE, UserRole.ADMIN))
):
    """
    Returns only events specifically assigned to this logged-in Judge.
    Strictly prevents seeing/scoring unassigned events.
    """
    if current_user.role == UserRole.ADMIN:
        events = db.query(Event).all()
        return [format_event_response(e) for e in events]

    assignments = db.query(JudgeAssignment).filter(JudgeAssignment.judge_id == current_user.id).all()
    event_ids = [a.event_id for a in assignments]
    events = db.query(Event).filter(Event.id.in_(event_ids)).all()
    return [format_event_response(e) for e in events]


@router.get("/event/{event_id}/assignments", response_model=List[JudgeAssignmentResponse])
def get_event_judge_assignments(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    assignments = db.query(JudgeAssignment).filter(JudgeAssignment.event_id == event_id).all()
    return [
        JudgeAssignmentResponse(
            id=a.id,
            event_id=a.event_id,
            event_title=a.event.title,
            judge_id=a.judge_id,
            judge_name=a.judge.full_name,
            round_id=a.round_id,
            round_name=a.round.name if a.round else None,
            status=a.status,
            assigned_at=a.assigned_at
        )
        for a in assignments
    ]


@router.post("/criteria", response_model=ScoreCriteriaResponse, status_code=status.HTTP_201_CREATED)
def create_score_criteria(
    req: ScoreCriteriaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    event = db.query(Event).filter(Event.id == req.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.role == UserRole.EVENT_COORDINATOR and event.coordinator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to set criteria for this event")

    criteria = ScoreCriteria(
        event_id=req.event_id,
        round_id=req.round_id,
        name=req.name.strip(),
        description=req.description,
        max_score=req.max_score,
        weightage=req.weightage
    )
    db.add(criteria)
    db.commit()
    db.refresh(criteria)
    return criteria


@router.get("/criteria/{event_id}", response_model=List[ScoreCriteriaResponse])
def get_event_criteria(
    event_id: int,
    round_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ScoreCriteria).filter(ScoreCriteria.event_id == event_id)
    if round_id:
        query = query.filter(ScoreCriteria.round_id == round_id)
    return query.all()
