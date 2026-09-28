from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.user import User, RoleEnum
from app.schemas.judging import (
    JudgeDashboardOut, JudgeEventTeamOut, EvaluationCreate, EvaluationOut, EventLeaderboardOut
)
from app.services.judging_service import JudgingService

router = APIRouter(tags=["Judging & Competitions"])


@router.get("/judge/dashboard", response_model=JudgeDashboardOut)
def get_judge_dashboard(
    current_user: User = Depends(require_role(RoleEnum.JUDGE, RoleEnum.ADMIN)),
    db: Session = Depends(get_db)
):
    """Judge dashboard listing assigned events, progress, and pending evaluations."""
    return JudgingService.get_judge_dashboard(db, current_user)


@router.get("/judge/events/{id}/teams", response_model=List[JudgeEventTeamOut])
def get_teams_to_evaluate(
    id: int,
    current_user: User = Depends(require_role(RoleEnum.JUDGE, RoleEnum.ADMIN)),
    db: Session = Depends(get_db)
):
    """List of participating teams for a competition and their evaluation status."""
    return JudgingService.get_teams_for_event(db, id, current_user)


@router.post("/judge/events/{id}/evaluations", response_model=EvaluationOut, status_code=status.HTTP_201_CREATED)
def submit_team_evaluation(
    id: int,
    eval_in: EvaluationCreate,
    current_user: User = Depends(require_role(RoleEnum.JUDGE, RoleEnum.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Submit or update score card for a team.
    Calculates total score (Innovation + Technical Execution + Presentation)
    and automatically triggers live ranking recalculation.
    """
    return JudgingService.submit_evaluation(db, id, current_user, eval_in)


class DirectEvaluationCreate(EvaluationCreate):
    event_id: int


@router.post("/judge/evaluations", response_model=EvaluationOut, status_code=status.HTTP_201_CREATED)
def submit_direct_evaluation(
    eval_in: DirectEvaluationCreate,
    current_user: User = Depends(require_role(RoleEnum.JUDGE, RoleEnum.ADMIN)),
    db: Session = Depends(get_db)
):
    """Direct judging evaluation endpoint matching friend's /api/judge/evaluations spec."""
    return JudgingService.submit_evaluation(db, eval_in.event_id, current_user, eval_in)


@router.get("/events/{id}/leaderboard", response_model=EventLeaderboardOut)
def get_event_leaderboard(id: int, db: Session = Depends(get_db)):
    """
    Live leaderboard endpoint. Ranks are computed dynamically from actual
    judge evaluations.
    """
    return JudgingService.get_leaderboard(db, id)


@router.post("/events/{id}/publish-results")
def publish_event_results(
    id: int,
    current_user: User = Depends(require_role(RoleEnum.COORDINATOR, RoleEnum.ADMIN)),
    db: Session = Depends(get_db)
):
    """Mark competition results as officially finalized and published."""
    JudgingService.publish_results(db, id)
    return {"message": "Results published successfully", "event_id": id}
