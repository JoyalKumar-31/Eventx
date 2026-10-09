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
from app.services.audit_service import log_action

router = APIRouter(prefix="/judges", tags=["Judging"])


def format_assignment_response(a: JudgeAssignment) -> JudgeAssignmentResponse:
    judge_user_data = {
        "id": a.judge.id,
        "full_name": a.judge.full_name,
        "email": a.judge.email,
        "role": a.judge.role.value if hasattr(a.judge.role, "value") else str(a.judge.role),
    } if a.judge else None

    return JudgeAssignmentResponse(
        id=a.id,
        event_id=a.event_id,
        event_title=a.event.title if a.event else f"Event #{a.event_id}",
        judge_id=a.judge_id,
        judge_name=a.judge.full_name if a.judge else f"Judge #{a.judge_id}",
        round_id=a.round_id,
        round_name=a.round.name if a.round else None,
        status=a.status,
        assigned_at=a.assigned_at,
        judge_user=judge_user_data
    )


@router.post("/assign", response_model=JudgeAssignmentResponse, status_code=status.HTTP_201_CREATED)
def assign_judge(
    req: JudgeAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    judge_target_id = req.judge_id or req.judge_user_id
    if not judge_target_id:
        raise HTTPException(status_code=400, detail="Missing judge_id or judge_user_id")

    assignment = assign_judge_to_event(
        db=db,
        event_id=req.event_id,
        judge_id=judge_target_id,
        round_id=req.round_id
    )
    return format_assignment_response(assignment)


@router.get("/my-events", response_model=List[EventListResponse])
def get_judge_assigned_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.JUDGE, UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    """
    Returns events specifically assigned to this logged-in Judge,
    or coordinated events if the caller is an Event Coordinator.
    """
    if current_user.role == UserRole.ADMIN:
        events = db.query(Event).all()
        return [format_event_response(e) for e in events]

    if current_user.role == UserRole.EVENT_COORDINATOR:
        events = db.query(Event).filter(Event.coordinator_id == current_user.id).all()
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
    return [format_assignment_response(a) for a in assignments]


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_200_OK)
def unassign_judge(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    assignment = db.query(JudgeAssignment).filter(JudgeAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Judge assignment not found")

    db.delete(assignment)
    db.commit()

    log_action(
        db,
        action="JUDGE_UNASSIGNED",
        entity_type="JudgeAssignment",
        entity_id=str(assignment_id),
        user_id=current_user.id,
        old_values={"judge_id": assignment.judge_id, "event_id": assignment.event_id}
    )
    return {"success": True, "message": "Judge assignment removed"}


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


@router.delete("/criteria/{criteria_id}", status_code=status.HTTP_200_OK)
def delete_score_criteria(
    criteria_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    criteria = db.query(ScoreCriteria).filter(ScoreCriteria.id == criteria_id).first()
    if not criteria:
        raise HTTPException(status_code=404, detail="Criteria not found")

    event = criteria.event
    if current_user.role == UserRole.EVENT_COORDINATOR and event.coordinator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to delete criteria for this event")

    db.delete(criteria)
    db.commit()
    return {"success": True, "message": "Criteria removed"}
