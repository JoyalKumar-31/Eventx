from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.enums import UserRole
from app.models.audit_log import AuditLog
from app.models.user import User
from app.models.judging import JudgeAssignment
from app.schemas.admin import (
    AdminDashboardStats,
    CoordinatorDashboardStats,
    JudgeDashboardStats,
    AuditLogResponse
)
from app.services.analytics_service import (
    get_admin_dashboard_metrics,
    get_coordinator_dashboard_metrics
)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/metrics", response_model=AdminDashboardStats)
def get_admin_metrics(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Real database aggregations for global fest administration."""
    metrics = get_admin_dashboard_metrics(db)
    return AdminDashboardStats(**metrics)


@router.get("/coordinator-metrics", response_model=CoordinatorDashboardStats)
def get_coordinator_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    metrics = get_coordinator_dashboard_metrics(db, current_user.id)
    return CoordinatorDashboardStats(**metrics)


@router.get("/judge-metrics", response_model=JudgeDashboardStats)
def get_judge_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.JUDGE, UserRole.ADMIN))
):
    assigned = db.query(JudgeAssignment).filter(JudgeAssignment.judge_id == current_user.id).count()
    completed = db.query(JudgeAssignment).filter(
        JudgeAssignment.judge_id == current_user.id,
        JudgeAssignment.status == "COMPLETED"
    ).count()

    return JudgeDashboardStats(
        assigned_events=assigned,
        pending_evaluations=max(0, assigned - completed),
        completed_evaluations=completed
    )


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

    results = []
    for log in logs:
        results.append(
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                user_name=log.user.full_name if log.user else "System/Guest",
                user_email=log.user.email if log.user else None,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                old_values=log.old_values,
                new_values=log.new_values,
                ip_address=log.ip_address,
                timestamp=log.timestamp
            )
        )
    return results
