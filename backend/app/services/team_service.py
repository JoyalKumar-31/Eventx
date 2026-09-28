import secrets
import string
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.team import Team, TeamMember, TeamInvitation
from app.models.event import Event
from app.models.user import User
from app.schemas.team import TeamCreate, TeamOut, TeamMemberOut
from app.schemas.student import UserBasicOut


class TeamService:
    @staticmethod
    def generate_team_code(prefix: str = "TM") -> str:
        rand_str = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return f"{prefix}-{rand_str}"

    @staticmethod
    def create_team(db: Session, user: User, team_in: TeamCreate) -> Team:
        event = db.query(Event).filter(Event.id == team_in.event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        if event.max_team_size <= 1:
            raise HTTPException(status_code=400, detail="This is an individual event, teams not allowed")

        # Check if user already leads or belongs to a team for this event
        existing_membership = db.query(TeamMember).join(TeamMember.team).filter(
            TeamMember.user_id == user.id,
            Team.event_id == event.id
        ).first()
        if existing_membership:
            raise HTTPException(status_code=400, detail="You already belong to a team for this event")

        prefix = ''.join(filter(str.isalnum, team_in.name))[:3].upper() or "FST"
        code = TeamService.generate_team_code(prefix)

        team = Team(
            name=team_in.name,
            event_id=event.id,
            leader_id=user.id,
            code=code,
            is_finalized=False
        )
        db.add(team)
        db.commit()
        db.refresh(team)

        # Add leader as first member
        leader_member = TeamMember(
            team_id=team.id,
            user_id=user.id
        )
        db.add(leader_member)
        db.commit()
        db.refresh(team)

        return team

    @staticmethod
    def join_team(db: Session, user: User, code: str) -> Team:
        team = db.query(Team).options(
            joinedload(Team.event),
            joinedload(Team.members)
        ).filter(Team.code == code.strip().upper()).first()

        if not team:
            raise HTTPException(status_code=404, detail="Invalid team code")

        event = team.event
        if len(team.members) >= event.max_team_size:
            raise HTTPException(status_code=400, detail=f"Team is already full (max {event.max_team_size} members)")

        # Check if user is already in this team
        if any(m.user_id == user.id for m in team.members):
            raise HTTPException(status_code=400, detail="You are already in this team")

        # Check if user is in another team for this event
        existing = db.query(TeamMember).join(TeamMember.team).filter(
            TeamMember.user_id == user.id,
            Team.event_id == event.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="You already belong to another team for this event")

        member = TeamMember(team_id=team.id, user_id=user.id)
        db.add(member)

        # Check if invitation exists and update status
        invitation = db.query(TeamInvitation).filter(
            TeamInvitation.team_id == team.id,
            TeamInvitation.invitee_id == user.id
        ).first()
        if invitation:
            invitation.status = "ACCEPTED"

        db.commit()
        db.refresh(team)
        return team

    @staticmethod
    def get_my_teams(db: Session, user: User) -> List[TeamOut]:
        # Teams where user is leader or member
        teams = db.query(Team).join(Team.members).options(
            joinedload(Team.event),
            joinedload(Team.leader),
            joinedload(Team.members).joinedload(TeamMember.user)
        ).filter(TeamMember.user_id == user.id).all()

        results = []
        for t in teams:
            members_out = [
                TeamMemberOut(
                    id=m.id,
                    user_id=m.user_id,
                    full_name=m.user.full_name,
                    email=m.user.email,
                    college=m.user.college,
                    joined_at=m.joined_at
                )
                for m in t.members
            ]
            results.append(
                TeamOut(
                    id=t.id,
                    name=t.name,
                    event_id=t.event_id,
                    event_name=t.event.name,
                    code=t.code,
                    is_finalized=t.is_finalized,
                    leader=UserBasicOut(id=t.leader.id, name=t.leader.full_name, email=t.leader.email, college=t.leader.college),
                    members=members_out,
                    created_at=t.created_at
                )
            )
        return results

    @staticmethod
    def invite_member(db: Session, team_id: int, user: User, invitee_email: str) -> TeamInvitation:
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        if team.leader_id != user.id:
            raise HTTPException(status_code=403, detail="Only team leader can invite members")

        invitee = db.query(User).filter(User.email == invitee_email.lower().strip()).first()
        if not invitee:
            raise HTTPException(status_code=404, detail="No registered student found with that email")

        # Check existing invitation
        existing_invite = db.query(TeamInvitation).filter(
            TeamInvitation.team_id == team.id,
            TeamInvitation.invitee_id == invitee.id
        ).first()
        if existing_invite:
            raise HTTPException(status_code=400, detail="Invitation already sent to this user")

        invitation = TeamInvitation(
            team_id=team.id,
            invitee_id=invitee.id,
            status="PENDING"
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        return invitation
