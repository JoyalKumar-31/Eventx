import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.enums import UserRole, TeamStatus, TeamMemberRole, RegistrationStatus
from app.models.event import Event
from app.models.registration import Team, TeamMember, Registration
from app.models.user import User
from app.schemas.registration import TeamCreate, TeamJoinRequest, TeamResponse, TeamMemberResponse
from app.services.qr_service import generate_qr_hash
from app.services.notification_service import create_notification

router = APIRouter(prefix="/teams", tags=["Teams"])


def format_team_response(team: Team) -> TeamResponse:
    members = [
        TeamMemberResponse(
            id=m.id,
            user_id=m.user_id,
            user_name=m.user.full_name if m.user else f"Member #{m.user_id}",
            user_email=m.user.email if m.user else "",
            role=m.role,
            joined_at=m.joined_at
        )
        for m in team.members
    ]

    is_reg = bool(team.registrations and len(team.registrations) > 0)
    reg_id = team.registrations[0].id if is_reg else None
    event_title = team.event.title if team.event else f"Event #{team.event_id}"
    min_size = team.event.min_team_size if team.event else 2
    max_size = team.event.max_team_size if team.event else 4
    fee = team.event.registration_fee if team.event else 0.0

    return TeamResponse(
        id=team.id,
        name=team.name,
        event_id=team.event_id,
        event_title=event_title,
        leader_id=team.leader_id,
        invite_code=team.invite_code,
        status=team.status,
        created_at=team.created_at,
        members=members,
        is_registered=is_reg,
        registration_id=reg_id,
        min_team_size=min_size,
        max_team_size=max_size,
        registration_fee=fee
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
        raise HTTPException(status_code=400, detail="You already lead a team squad for this event.")

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

    # If the team was already registered for the competition, automatically register this new member too!
    existing_team_reg = db.query(Registration).filter(
        Registration.event_id == event.id,
        Registration.team_id == team.id
    ).first()

    if existing_team_reg:
        reg_check = db.query(Registration).filter(
            Registration.event_id == event.id,
            Registration.user_id == current_user.id
        ).first()

        if not reg_check:
            reg_num = f"REG-{event.id:03d}-{uuid.uuid4().hex[:6].upper()}"
            qr_token = generate_qr_hash(reg_num, event.id, current_user.id)
            new_reg = Registration(
                registration_number=reg_num,
                event_id=event.id,
                user_id=current_user.id,
                team_id=team.id,
                status=existing_team_reg.status,
                qr_code_hash=qr_token
            )
            db.add(new_reg)
            event.current_participants += 1

            create_notification(
                db,
                user_id=current_user.id,
                title="Entry Pass Generated",
                message=f"You joined '{team.name}'. Your entry pass for '{event.title}' is now ready.",
                link="/student/passes"
            )

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


@router.get("/event/{event_id}", response_model=List[TeamResponse])
def get_event_teams(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN, UserRole.JUDGE))
):
    """
    Returns all squads formed or registered for a specific event.
    """
    teams = db.query(Team).filter(Team.event_id == event_id).order_by(Team.created_at.desc()).all()
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
