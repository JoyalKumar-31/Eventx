from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.judging import JudgeAssignment, Evaluation, EventResult
from app.models.event import Event
from app.models.team import Team, TeamMember
from app.models.user import User, RoleEnum
from app.schemas.judging import (
    EvaluationCreate, EvaluationOut, EventLeaderboardOut, LeaderboardEntryOut, JudgeDashboardOut, JudgeEventTeamOut
)


class JudgingService:
    @staticmethod
    def get_judge_dashboard(db: Session, judge: User) -> JudgeDashboardOut:
        # Get assigned events
        assignments = db.query(JudgeAssignment).options(
            joinedload(JudgeAssignment.event)
        ).filter(JudgeAssignment.judge_id == judge.id).all()

        assigned_list = []
        for a in assignments:
            ev = a.event
            total_teams = db.query(func.count(Team.id)).filter(Team.event_id == ev.id).scalar() or 0
            evaluated_teams = db.query(func.count(Evaluation.id)).filter(
                Evaluation.event_id == ev.id,
                Evaluation.judge_id == judge.id
            ).scalar() or 0

            assigned_list.append({
                "event_id": ev.id,
                "event_name": ev.name,
                "event_date": str(ev.event_date),
                "total_teams": total_teams,
                "evaluated_teams": evaluated_teams,
                "pending_teams": max(0, total_teams - evaluated_teams),
                "status": ev.status
            })

        return JudgeDashboardOut(
            judge_name=judge.full_name,
            assigned_events=assigned_list
        )

    @staticmethod
    def get_teams_for_event(db: Session, event_id: int, judge: User) -> List[JudgeEventTeamOut]:
        # Check event exists
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        teams = db.query(Team).options(
            joinedload(Team.members)
        ).filter(Team.event_id == event_id).all()

        results = []
        for t in teams:
            eval_record = db.query(Evaluation).filter(
                Evaluation.event_id == event_id,
                Evaluation.team_id == t.id,
                Evaluation.judge_id == judge.id
            ).first()

            eval_out = None
            if eval_record:
                eval_out = EvaluationOut(
                    id=eval_record.id,
                    team_id=t.id,
                    team_name=t.name,
                    judge_name=judge.full_name,
                    innovation=eval_record.innovation,
                    technical_execution=eval_record.technical_execution,
                    presentation=eval_record.presentation,
                    total_score=eval_record.total_score,
                    remarks=eval_record.remarks
                )

            results.append(
                JudgeEventTeamOut(
                    id=t.id,
                    name=t.name,
                    members_count=len(t.members),
                    is_evaluated=eval_record is not None,
                    evaluation=eval_out
                )
            )

        return results

    @staticmethod
    def submit_evaluation(
        db: Session,
        event_id: int,
        judge: User,
        eval_in: EvaluationCreate
    ) -> EvaluationOut:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        team = db.query(Team).filter(Team.id == eval_in.team_id, Team.event_id == event_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team does not belong to this event")

        # Compute total
        total = round(eval_in.innovation + eval_in.technical_execution + eval_in.presentation, 2)

        evaluation = db.query(Evaluation).filter(
            Evaluation.event_id == event_id,
            Evaluation.team_id == team.id,
            Evaluation.judge_id == judge.id
        ).first()

        if evaluation:
            # Update existing evaluation
            evaluation.innovation = eval_in.innovation
            evaluation.technical_execution = eval_in.technical_execution
            evaluation.presentation = eval_in.presentation
            evaluation.total_score = total
            evaluation.remarks = eval_in.remarks
            evaluation.submitted_at = datetime.now(timezone.utc)
        else:
            # Create new evaluation
            evaluation = Evaluation(
                event_id=event_id,
                team_id=team.id,
                judge_id=judge.id,
                innovation=eval_in.innovation,
                technical_execution=eval_in.technical_execution,
                presentation=eval_in.presentation,
                total_score=total,
                remarks=eval_in.remarks
            )
            db.add(evaluation)

        db.commit()
        db.refresh(evaluation)

        # Trigger automatic leaderboard recalculation
        JudgingService.recalculate_event_results(db, event_id)

        return EvaluationOut(
            id=evaluation.id,
            team_id=team.id,
            team_name=team.name,
            judge_name=judge.full_name,
            innovation=evaluation.innovation,
            technical_execution=evaluation.technical_execution,
            presentation=evaluation.presentation,
            total_score=evaluation.total_score,
            remarks=evaluation.remarks
        )

    @staticmethod
    def recalculate_event_results(db: Session, event_id: int):
        """
        Recalculates average scores and ranks across all judges.
        """
        # Average total_score per team
        scores = db.query(
            Evaluation.team_id,
            func.avg(Evaluation.total_score).label("avg_score"),
            func.count(Evaluation.id).label("eval_count")
        ).filter(
            Evaluation.event_id == event_id
        ).group_by(Evaluation.team_id).order_by(func.avg(Evaluation.total_score).desc()).all()

        for rank_idx, s in enumerate(scores, start=1):
            team_result = db.query(EventResult).filter(
                EventResult.event_id == event_id,
                EventResult.team_id == s.team_id
            ).first()

            if team_result:
                team_result.rank = rank_idx
                team_result.average_score = round(float(s.avg_score), 2)
                team_result.total_evaluations = s.eval_count
            else:
                team_result = EventResult(
                    event_id=event_id,
                    team_id=s.team_id,
                    rank=rank_idx,
                    average_score=round(float(s.avg_score), 2),
                    total_evaluations=s.eval_count,
                    is_published=False
                )
                db.add(team_result)
        db.commit()

    @staticmethod
    def get_leaderboard(db: Session, event_id: int) -> EventLeaderboardOut:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Query live computed scores if any evaluations exist
        results = db.query(EventResult).options(
            joinedload(EventResult.team)
        ).filter(EventResult.event_id == event_id).order_by(EventResult.rank.asc()).all()

        is_published = any(r.is_published for r in results) if results else False

        entries = [
            LeaderboardEntryOut(
                rank=r.rank,
                team_id=r.team_id,
                team_name=r.team.name if r.team else f"Team {r.team_id}",
                score=round(float(r.average_score), 2),
                evaluations_count=r.total_evaluations
            )
            for r in results
        ]

        return EventLeaderboardOut(
            event_id=event.id,
            event_name=event.name,
            is_published=is_published,
            leaderboard=entries
        )

    @staticmethod
    def publish_results(db: Session, event_id: int) -> bool:
        results = db.query(EventResult).filter(EventResult.event_id == event_id).all()
        now = datetime.now()
        for r in results:
            r.is_published = True
            r.published_at = now
        db.commit()
        return True
