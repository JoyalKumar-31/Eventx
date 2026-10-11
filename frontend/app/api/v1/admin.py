from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.enums import UserRole, ApplicationStatus, InvitationStatus
from app.models.audit_log import AuditLog
from app.models.user import User
from app.models.judging import JudgeAssignment
from app.schemas.admin import (
    AdminDashboardStats,
    CoordinatorDashboardStats,
    JudgeDashboardStats,
    AuditLogResponse
)
from app.schemas.application import (
    CoordinatorApplicationResponse,
    JudgeApplicationResponse,
    InvitationCreateRequest,
    InvitationResponse,
    ApplicationReviewRequest
)
from app.services.analytics_service import (
    get_admin_dashboard_metrics,
    get_coordinator_dashboard_metrics
)
from app.services.application_service import (
    list_coordinator_applications,
    approve_coordinator_application,
    reject_coordinator_application,
    list_judge_applications,
    approve_judge_application,
    reject_judge_application,
    create_invitation,
    list_invitations,
    revoke_invitation
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


# ==============================================================================
# ADMIN ROLE WORKFLOW: COORDINATOR APPLICATIONS REVIEW
# ==============================================================================

@router.get("/applications/coordinators", response_model=List[CoordinatorApplicationResponse])
def get_coordinator_applications(
    status: Optional[ApplicationStatus] = Query(None, description="Filter by status: PENDING, APPROVED, REJECTED"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Lists all coordinator applications for administrator review.
    """
    apps = list_coordinator_applications(db=db, status_filter=status)
    return [CoordinatorApplicationResponse.model_validate(a) for a in apps]


@router.post("/applications/coordinators/{application_id}/approve", response_model=CoordinatorApplicationResponse)
def approve_coordinator(
    application_id: int,
    req: ApplicationReviewRequest = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Approves an Event Coordinator application and assigns the EVENT_COORDINATOR role to the user.
    """
    notes = req.admin_notes if req else None
    app = approve_coordinator_application(db=db, application_id=application_id, admin_user=admin_user, admin_notes=notes)
    return CoordinatorApplicationResponse.model_validate(app)


@router.post("/applications/coordinators/{application_id}/reject", response_model=CoordinatorApplicationResponse)
def reject_coordinator(
    application_id: int,
    req: ApplicationReviewRequest = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Rejects an Event Coordinator application with optional reason notes.
    """
    notes = req.admin_notes if req else None
    app = reject_coordinator_application(db=db, application_id=application_id, admin_user=admin_user, admin_notes=notes)
    return CoordinatorApplicationResponse.model_validate(app)


# ==============================================================================
# ADMIN ROLE WORKFLOW: JUDGE APPLICATIONS REVIEW
# ==============================================================================

@router.get("/applications/judges", response_model=List[JudgeApplicationResponse])
def get_judge_applications(
    status: Optional[ApplicationStatus] = Query(None, description="Filter by status: PENDING, APPROVED, REJECTED"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Lists all fest judge applications for administrator review.
    """
    apps = list_judge_applications(db=db, status_filter=status)
    return [JudgeApplicationResponse.model_validate(a) for a in apps]


@router.post("/applications/judges/{application_id}/approve", response_model=JudgeApplicationResponse)
def approve_judge(
    application_id: int,
    req: ApplicationReviewRequest = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Approves a Fest Judge application and assigns the JUDGE role to the user.
    """
    notes = req.admin_notes if req else None
    app = approve_judge_application(db=db, application_id=application_id, admin_user=admin_user, admin_notes=notes)
    return JudgeApplicationResponse.model_validate(app)


@router.post("/applications/judges/{application_id}/reject", response_model=JudgeApplicationResponse)
def reject_judge(
    application_id: int,
    req: ApplicationReviewRequest = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Rejects a Fest Judge application with optional reason notes.
    """
    notes = req.admin_notes if req else None
    app = reject_judge_application(db=db, application_id=application_id, admin_user=admin_user, admin_notes=notes)
    return JudgeApplicationResponse.model_validate(app)


# ==============================================================================
# ADMIN ROLE WORKFLOW: JUDGE & SPONSOR INVITATIONS
# ==============================================================================

@router.post("/invitations", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
def create_role_invitation(
    req: InvitationCreateRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Issues a cryptographically secure single-use invitation token for a Judge or Sponsor.
    """
    inv, raw_token = create_invitation(db=db, req=req, admin_user=admin_user)
    resp = InvitationResponse.model_validate(inv)
    resp.raw_token = raw_token
    resp.invite_url = f"/invite/accept?token={raw_token}"
    return resp


@router.get("/invitations", response_model=List[InvitationResponse])
def get_role_invitations(
    role: Optional[UserRole] = Query(None, description="Filter by role: JUDGE, SPONSOR"),
    status: Optional[InvitationStatus] = Query(None, description="Filter by status: PENDING, ACCEPTED, EXPIRED, REVOKED"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Lists all administrator-created role invitations.
    """
    invs = list_invitations(db=db, role_filter=role, status_filter=status)
    return [InvitationResponse.model_validate(i) for i in invs]


@router.delete("/invitations/{invitation_id}", response_model=InvitationResponse)
def revoke_role_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Revokes a pending role invitation, invalidating its token.
    """
    inv = revoke_invitation(db=db, invitation_id=invitation_id, admin_user=admin_user)
    return InvitationResponse.model_validate(inv)

