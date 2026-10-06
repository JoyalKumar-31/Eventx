import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.enums import UserRole, TeamStatus, TeamMemberRole
from app.models.event import Event
from app.models.registration import Team, TeamMember
from app.models.user import User
from app.schemas.registration import TeamCreate, TeamJoinRequest, TeamResponse, TeamMemberResponse

router = APIRouter(prefix="/teams", tags=["Teams"])


def format_team_response(team: Team) -> TeamResponse:
    members = [
        TeamMemberResponse(
            id=m.id,
            user_id=m.user_id,
            user_name=m.user.full_name,
            user_email=m.user.email,
            role=m.role,
            joined_at=m.joined_at
        )
        for m in team.members
    ]
    return TeamResponse(
        id=team.id,
        name=team.name,
        event_id=team.event_id,
        leader_id=team.leader_id,
        invite_code=team.invite_code,
        status=team.status,
        created_at=team.created_at,
        members=members
    )


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    req: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT, UserRole.ADMIN))
):
    event = db.query(Event).filter(Event.id == req.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if not event.is_team_event:
        raise HTTPException(status_code=400, detail="This is an individual event, not a team event.")

    # Check if user already leads a team for this event
    existing_leader = db.query(Team).filter(Team.event_id == req.event_id, Team.leader_id == current_user.id).first()
    if existing_leader:
        raise HTTPException(status_code=400, detail="You already lead a team for this event.")

    invite_code = f"FEST-{uuid.uuid4().hex[:6].upper()}"

    team = Team(
        name=req.name.strip(),
        event_id=event.id,
        leader_id=current_user.id,
        invite_code=invite_code,
        status=TeamStatus.FORMING
    )
    db.add(team)
    db.flush()

    # Add leader as first member
    leader_member = TeamMember(
        team_id=team.id,
        user_id=current_user.id,
        role=TeamMemberRole.LEADER
    )
    db.add(leader_member)

    db.commit()
    db.refresh(team)
    return format_team_response(team)


@router.post("/join", response_model=TeamResponse)
def join_team(
    req: TeamJoinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT, UserRole.ADMIN))
):
    code = req.invite_code.strip().upper()
    team = db.query(Team).filter(Team.invite_code == code).first()
    if not team:
        raise HTTPException(status_code=404, detail="Invalid team invite code")

    event = team.event
    if len(team.members) >= event.max_team_size:
        raise HTTPException(status_code=400, detail="This team has already reached its maximum allowed members.")

    # Check if user is already a member
    already_in_team = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == current_user.id).first()
    if already_in_team:
        raise HTTPException(status_code=400, detail="You are already a member of this team.")

    new_member = TeamMember(
        team_id=team.id,
        user_id=current_user.id,
        role=TeamMemberRole.MEMBER
    )
    db.add(new_member)

    if len(team.members) + 1 >= event.min_team_size:
        team.status = TeamStatus.COMPLETE

    db.commit()
    db.refresh(team)
    return format_team_response(team)


@router.get("/my", response_model=List[TeamResponse])
def get_my_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    team_memberships = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).all()
    team_ids = [tm.team_id for tm in team_memberships]
    teams = db.query(Team).filter(Team.id.in_(team_ids)).all()
    return [format_team_response(t) for t in teams]


@router.get("/{team_id}", response_model=TeamResponse)
def get_team_detail(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return format_team_response(team)
