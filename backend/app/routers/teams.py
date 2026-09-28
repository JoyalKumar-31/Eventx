from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.team import (
    TeamCreate, TeamJoin, TeamOut, TeamInvitationCreate, TeamInvitationOut
)
from app.services.team_service import TeamService

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post("", response_model=TeamOut, status_code=status.HTTP_201_CREATED)
def create_team(
    team_in: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new team for a group competition."""
    created = TeamService.create_team(db, current_user, team_in)
    teams = TeamService.get_my_teams(db, current_user)
    return next((t for t in teams if t.id == created.id), None)


@router.post("/join", response_model=TeamOut)
def join_team(
    join_in: TeamJoin,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join an existing team using its invite code."""
    joined = TeamService.join_team(db, current_user, join_in.code)
    teams = TeamService.get_my_teams(db, current_user)
    return next((t for t in teams if t.id == joined.id), None)


@router.get("/my", response_model=List[TeamOut])
def get_my_teams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all teams that the student is a member or leader of."""
    return TeamService.get_my_teams(db, current_user)


@router.post("/{id}/invite", response_model=TeamInvitationOut)
def invite_team_member(
    id: int,
    invite_in: TeamInvitationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invite another student to join a team."""
    invite = TeamService.invite_member(db, id, current_user, invite_in.email)
    return TeamInvitationOut(
        id=invite.id,
        team_id=invite.team_id,
        team_name=invite.team.name,
        event_name=invite.team.event.name,
        status=invite.status,
        created_at=invite.created_at
    )
