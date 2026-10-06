from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, get_current_user_optional, require_role
from app.models.enums import UserRole
from app.models.event import Event
from app.models.judging import Result
from app.models.user import User
from app.schemas.judging import ResultResponse, LeaderboardEntry
from app.services.judging_service import calculate_event_leaderboard, publish_event_results

router = APIRouter(prefix="/results", tags=["Results"])


def format_result(res: Result) -> ResultResponse:
    reg = res.registration
    return ResultResponse(
        id=res.id,
        event_id=res.event_id,
        event_title=res.event.title,
        registration_id=res.registration_id,
        participant_name=reg.user.full_name,
        team_name=reg.team.name if reg.team else None,
        rank=res.rank,
        total_score=res.total_score,
        award_title=res.award_title,
        is_published=res.is_published,
        published_at=res.published_at
    )


@router.get("/leaderboard/{event_id}", response_model=List[LeaderboardEntry])
def get_leaderboard(
    event_id: int,
    round_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN, UserRole.JUDGE))
):
    """
    Auto-computes dynamic leaderboard for judging review before publication.
    """
    leaderboard = calculate_event_leaderboard(db, event_id, round_id)
    return [
        LeaderboardEntry(
            registration_id=item["registration_id"],
            participant_name=item["participant_name"],
            team_name=item["team_name"],
            total_score=item["total_score"],
            rank=item["rank"]
        )
        for item in leaderboard
    ]


@router.post("/publish/{event_id}", response_model=List[ResultResponse])
def publish_results(
    event_id: int,
    round_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    """
    Finalizes and publishes results, computes ranks, generates certificates, and sends notifications.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.role == UserRole.EVENT_COORDINATOR and event.coordinator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to publish results for this event")

    results = publish_event_results(
        db=db,
        event_id=event_id,
        published_by_user_id=current_user.id,
        round_id=round_id
    )
    return [format_result(r) for r in results]


@router.get("/public/{event_id}", response_model=List[ResultResponse])
def get_public_results(
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    Public result listing. Only published results are visible.
    """
    results = db.query(Result).filter(
        Result.event_id == event_id,
        Result.is_published == True
    ).order_by(Result.rank.asc()).all()
    return [format_result(r) for r in results]


@router.get("/public", response_model=List[ResultResponse])
def list_all_public_results(
    db: Session = Depends(get_db)
):
    """
    All published winners and results across fest events.
    """
    results = db.query(Result).filter(Result.is_published == True).order_by(Result.event_id.asc(), Result.rank.asc()).all()
    return [format_result(r) for r in results]
