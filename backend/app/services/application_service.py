import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.enums import UserRole, ApplicationStatus, InvitationStatus
from app.models.user import (
    User,
    CoordinatorProfile,
    JudgeProfile,
    SponsorProfile,
)
from app.models.application import (
    CoordinatorApplication,
    JudgeApplication,
    SponsorApplication,
    Invitation,
)
from app.schemas.application import (
    CoordinatorApplyRequest,
    JudgeApplyRequest,
    SponsorApplyRequest,
    InvitationCreateRequest,
    InvitationAcceptRequest,
)
from app.schemas.auth import TokenResponse, UserInfo
from app.services.audit_service import log_action
from app.services.notification_service import create_notification


# ==============================================================================
# WORKFLOW B: EVENT COORDINATOR APPLICATION & APPROVAL
# ==============================================================================

def apply_coordinator(
    db: Session,
    req: CoordinatorApplyRequest,
    ip_address: Optional[str] = None
) -> CoordinatorApplication:
    email_clean = req.email.lower().strip()

    # Check for existing pending application
    existing_pending = db.query(CoordinatorApplication).filter(
        CoordinatorApplication.email == email_clean,
        CoordinatorApplication.status == ApplicationStatus.PENDING
    ).first()
    if existing_pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "message": "A pending Coordinator application already exists for this email address.", "error_code": "APPLICATION_PENDING"}
        )

    # Check if user already exists
    user = db.query(User).filter(User.email == email_clean).first()
    if user:
        if user.role in [UserRole.EVENT_COORDINATOR, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"success": False, "message": "This account already holds Event Coordinator or Administrator privileges.", "error_code": "ALREADY_PRIVILEGED"}
            )
    else:
        # Create base account with STUDENT role (unprivileged until approved)
        if not req.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"success": False, "message": "Password is required to set up your applicant account.", "error_code": "PASSWORD_REQUIRED"}
            )
        user = User(
            email=email_clean,
            hashed_password=hash_password(req.password),
            full_name=req.full_name.strip(),
            role=UserRole.STUDENT,  # STRICT: Unprivileged base role
            phone=req.phone,
            is_active=True
        )
        db.add(user)
        db.flush()

    # Create application with PENDING status
    application = CoordinatorApplication(
        user_id=user.id,
        full_name=req.full_name.strip(),
        email=email_clean,
        phone=req.phone,
        department=req.department.strip(),
        designation=req.designation.strip(),
        experience=req.experience.strip() if req.experience else None,
        office_location=req.office_location.strip() if req.office_location else None,
        status=ApplicationStatus.PENDING
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    log_action(
        db,
        action="COORDINATOR_APPLICATION_SUBMITTED",
        entity_type="CoordinatorApplication",
        entity_id=str(application.id),
        user_id=user.id,
        new_values={"email": email_clean, "department": req.department, "status": ApplicationStatus.PENDING.value},
        ip_address=ip_address
    )

    create_notification(
        db,
        user_id=user.id,
        title="Coordinator Application Submitted",
        message="Your application for Event Coordinator has been received and is pending administrative review."
    )

    return application


def list_coordinator_applications(
    db: Session,
    status_filter: Optional[ApplicationStatus] = None
) -> List[CoordinatorApplication]:
    query = db.query(CoordinatorApplication)
    if status_filter:
        query = query.filter(CoordinatorApplication.status == status_filter)
    return query.order_by(CoordinatorApplication.created_at.desc()).all()


def approve_coordinator_application(
    db: Session,
    application_id: int,
    admin_user: User,
    admin_notes: Optional[str] = None
) -> CoordinatorApplication:
    application = db.query(CoordinatorApplication).filter(CoordinatorApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": "Application not found", "error_code": "NOT_FOUND"}
        )

    # Prevent self-approval
    if application.user_id == admin_user.id or application.email == admin_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": "Administrators cannot approve their own coordinator application.", "error_code": "SELF_APPROVAL_FORBIDDEN"}
        )

    if application.status == ApplicationStatus.APPROVED:
        return application

    # Update application
    now = datetime.now(timezone.utc)
    application.status = ApplicationStatus.APPROVED
    application.reviewed_by_id = admin_user.id
    application.reviewed_at = now
    if admin_notes:
        application.admin_notes = admin_notes

    # Find or link user
    user = db.query(User).filter(User.id == application.user_id).first() if application.user_id else None
    if not user:
        user = db.query(User).filter(User.email == application.email).first()

    if user:
        user.role = UserRole.EVENT_COORDINATOR

        # Upsert CoordinatorProfile
        cp = db.query(CoordinatorProfile).filter(CoordinatorProfile.user_id == user.id).first()
        if not cp:
            cp = CoordinatorProfile(
                user_id=user.id,
                department=application.department,
                designation=application.designation,
                office_location=application.office_location
            )
            db.add(cp)
        else:
            cp.department = application.department
            cp.designation = application.designation
            if application.office_location:
                cp.office_location = application.office_location

        create_notification(
            db,
            user_id=user.id,
            title="Coordinator Application Approved!",
            message=f"Congratulations {user.full_name}! Your Event Coordinator application has been approved. You now have access to coordinator features."
        )

    db.commit()
    db.refresh(application)

    log_action(
        db,
        action="COORDINATOR_APPLICATION_APPROVED",
        entity_type="CoordinatorApplication",
        entity_id=str(application.id),
        user_id=admin_user.id,
        new_values={"applicant_email": application.email, "promoted_user_id": user.id if user else None}
    )

    return application


def reject_coordinator_application(
    db: Session,
    application_id: int,
    admin_user: User,
    admin_notes: Optional[str] = None
) -> CoordinatorApplication:
    application = db.query(CoordinatorApplication).filter(CoordinatorApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": "Application not found", "error_code": "NOT_FOUND"}
        )

    if application.user_id == admin_user.id or application.email == admin_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": "Cannot reject your own application.", "error_code": "SELF_REJECTION_FORBIDDEN"}
        )

    now = datetime.now(timezone.utc)
    application.status = ApplicationStatus.REJECTED
    application.reviewed_by_id = admin_user.id
    application.reviewed_at = now
    if admin_notes:
        application.admin_notes = admin_notes

    # Keep user role unchanged as STUDENT
    if application.user_id:
        create_notification(
            db,
            user_id=application.user_id,
            title="Coordinator Application Update",
            message=f"Your Event Coordinator application was reviewed. Status: Rejected. Reason: {admin_notes or 'Requirements not met at this time.'}"
        )

    db.commit()
    db.refresh(application)

    log_action(
        db,
        action="COORDINATOR_APPLICATION_REJECTED",
        entity_type="CoordinatorApplication",
        entity_id=str(application.id),
        user_id=admin_user.id,
        new_values={"applicant_email": application.email, "admin_notes": admin_notes}
    )

    return application


# ==============================================================================
# WORKFLOW C: FEST JUDGE APPLICATION & APPROVAL (SAME AS COORDINATOR)
# ==============================================================================

def apply_judge(
    db: Session,
    req: JudgeApplyRequest,
    ip_address: Optional[str] = None
) -> JudgeApplication:
    email_clean = req.email.lower().strip()

    # Check for existing pending application
    existing_pending = db.query(JudgeApplication).filter(
        JudgeApplication.email == email_clean,
        JudgeApplication.status == ApplicationStatus.PENDING
    ).first()
    if existing_pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "message": "A pending Judge application already exists for this email address.", "error_code": "APPLICATION_PENDING"}
        )

    # Check if user already exists
    user = db.query(User).filter(User.email == email_clean).first()
    if user:
        if user.role in [UserRole.JUDGE, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"success": False, "message": f"User is already registered with role {user.role.value}.", "error_code": "ROLE_ALREADY_ASSIGNED"}
            )
    else:
        # Create user account with STUDENT role (safe default; unapproved)
        if not req.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"success": False, "message": "Password is required to set up your applicant account.", "error_code": "PASSWORD_REQUIRED"}
            )
        user = User(
            email=email_clean,
            hashed_password=hash_password(req.password),
            full_name=req.full_name.strip(),
            role=UserRole.STUDENT,  # STRICT: Unprivileged base role
            phone=req.phone,
            is_active=True
        )
        db.add(user)
        db.flush()

    # Create application with PENDING status
    application = JudgeApplication(
        user_id=user.id,
        full_name=req.full_name.strip(),
        email=email_clean,
        phone=req.phone,
        organization=req.organization.strip(),
        specialization=req.specialization.strip(),
        experience=req.experience.strip() if req.experience else None,
        bio=req.bio.strip() if req.bio else None,
        status=ApplicationStatus.PENDING
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    log_action(
        db,
        action="JUDGE_APPLICATION_SUBMITTED",
        entity_type="JudgeApplication",
        entity_id=str(application.id),
        user_id=user.id,
        new_values={"email": email_clean, "organization": req.organization, "specialization": req.specialization, "status": ApplicationStatus.PENDING.value},
        ip_address=ip_address
    )

    create_notification(
        db,
        user_id=user.id,
        title="Judge Application Submitted",
        message="Your application for Fest Judge has been received and is pending administrative review."
    )

    return application


def list_judge_applications(
    db: Session,
    status_filter: Optional[ApplicationStatus] = None
) -> List[JudgeApplication]:
    query = db.query(JudgeApplication)
    if status_filter:
        query = query.filter(JudgeApplication.status == status_filter)
    return query.order_by(JudgeApplication.created_at.desc()).all()


def approve_judge_application(
    db: Session,
    application_id: int,
    admin_user: User,
    admin_notes: Optional[str] = None
) -> JudgeApplication:
    application = db.query(JudgeApplication).filter(JudgeApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": "Application not found", "error_code": "NOT_FOUND"}
        )

    # Prevent self-approval
    if application.user_id == admin_user.id or application.email == admin_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": "Administrators cannot approve their own judge application.", "error_code": "SELF_APPROVAL_FORBIDDEN"}
        )

    if application.status == ApplicationStatus.APPROVED:
        return application

    # Update application
    now = datetime.now(timezone.utc)
    application.status = ApplicationStatus.APPROVED
    application.reviewed_by_id = admin_user.id
    application.reviewed_at = now
    if admin_notes:
        application.admin_notes = admin_notes

    # Find or link user
    user = db.query(User).filter(User.id == application.user_id).first() if application.user_id else None
    if not user:
        user = db.query(User).filter(User.email == application.email).first()

    if user:
        user.role = UserRole.JUDGE

        # Upsert JudgeProfile
        jp = db.query(JudgeProfile).filter(JudgeProfile.user_id == user.id).first()
        if not jp:
            jp = JudgeProfile(
                user_id=user.id,
                organization=application.organization,
                specialization=application.specialization,
                bio=application.bio
            )
            db.add(jp)
        else:
            jp.organization = application.organization
            jp.specialization = application.specialization
            if application.bio:
                jp.bio = application.bio

        create_notification(
            db,
            user_id=user.id,
            title="Judge Application Approved!",
            message=f"Congratulations {user.full_name}! Your Fest Judge application has been approved. You are now authorized as a Fest Judge."
        )

    db.commit()
    db.refresh(application)

    log_action(
        db,
        action="JUDGE_APPLICATION_APPROVED",
        entity_type="JudgeApplication",
        entity_id=str(application.id),
        user_id=admin_user.id,
        new_values={"applicant_email": application.email, "promoted_user_id": user.id if user else None}
    )

    return application


def reject_judge_application(
    db: Session,
    application_id: int,
    admin_user: User,
    admin_notes: Optional[str] = None
) -> JudgeApplication:
    application = db.query(JudgeApplication).filter(JudgeApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": "Application not found", "error_code": "NOT_FOUND"}
        )

    if application.user_id == admin_user.id or application.email == admin_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": "Cannot reject your own application.", "error_code": "SELF_REJECTION_FORBIDDEN"}
        )

    now = datetime.now(timezone.utc)
    application.status = ApplicationStatus.REJECTED
    application.reviewed_by_id = admin_user.id
    application.reviewed_at = now
    if admin_notes:
        application.admin_notes = admin_notes

    # Keep user role unchanged as STUDENT
    if application.user_id:
        create_notification(
            db,
            user_id=application.user_id,
            title="Judge Application Update",
            message=f"Your Fest Judge application was reviewed. Status: Rejected. Reason: {admin_notes or 'Requirements not met at this time.'}"
        )

    db.commit()
    db.refresh(application)

    log_action(
        db,
        action="JUDGE_APPLICATION_REJECTED",
        entity_type="JudgeApplication",
        entity_id=str(application.id),
        user_id=admin_user.id,
        new_values={"applicant_email": application.email, "admin_notes": admin_notes}
    )

    return application


# ==============================================================================
# WORKFLOW D: INVITATIONS
# ==============================================================================

def create_invitation(
    db: Session,
    req: InvitationCreateRequest,
    admin_user: User
) -> Tuple[Invitation, str]:
    if req.role not in [UserRole.JUDGE, UserRole.SPONSOR]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "Invitations can only be issued for JUDGE or SPONSOR roles.", "error_code": "INVALID_INVITATION_ROLE"}
        )

    email_clean = req.email.lower().strip()

    # Generate single-use cryptographically secure random token (32 URL-safe bytes)
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    # Revoke any prior pending invitation for same email and role
    db.query(Invitation).filter(
        Invitation.email == email_clean,
        Invitation.role == req.role,
        Invitation.status == InvitationStatus.PENDING
    ).update({"status": InvitationStatus.REVOKED})

    expires_at = datetime.now(timezone.utc) + timedelta(days=req.expires_in_days)

    invitation = Invitation(
        email=email_clean,
        role=req.role,
        token_hash=token_hash,
        status=InvitationStatus.PENDING,
        organization=req.organization.strip() if req.organization else None,
        specialization=req.specialization.strip() if req.specialization else None,
        invited_by_id=admin_user.id,
        expires_at=expires_at
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    log_action(
        db,
        action="INVITATION_CREATED",
        entity_type="Invitation",
        entity_id=str(invitation.id),
        user_id=admin_user.id,
        new_values={"email": email_clean, "role": req.role.value, "expires_at": expires_at.isoformat()}
    )

    return invitation, raw_token


def list_invitations(
    db: Session,
    role_filter: Optional[UserRole] = None,
    status_filter: Optional[InvitationStatus] = None
) -> List[Invitation]:
    query = db.query(Invitation)
    if role_filter:
        query = query.filter(Invitation.role == role_filter)
    if status_filter:
        query = query.filter(Invitation.status == status_filter)
    return query.order_by(Invitation.created_at.desc()).all()


def revoke_invitation(db: Session, invitation_id: int, admin_user: User) -> Invitation:
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")

    invitation.status = InvitationStatus.REVOKED
    db.commit()
    db.refresh(invitation)

    log_action(
        db,
        action="INVITATION_REVOKED",
        entity_type="Invitation",
        entity_id=str(invitation.id),
        user_id=admin_user.id,
        new_values={"email": invitation.email, "status": InvitationStatus.REVOKED.value}
    )
    return invitation


def verify_invitation_token(db: Session, raw_token: str) -> Invitation:
    token_clean = raw_token.strip()
    token_hash = hashlib.sha256(token_clean.encode("utf-8")).hexdigest()

    invitation = db.query(Invitation).filter(Invitation.token_hash == token_hash).first()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "Invalid invitation code or link.", "error_code": "INVALID_TOKEN"}
        )

    if invitation.status == InvitationStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "This invitation has already been accepted and cannot be reused.", "error_code": "TOKEN_ALREADY_USED"}
        )

    if invitation.status == InvitationStatus.REVOKED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "This invitation has been revoked by an administrator.", "error_code": "TOKEN_REVOKED"}
        )

    # Check expiry
    now_utc = datetime.now(timezone.utc)
    exp = invitation.expires_at if invitation.expires_at.tzinfo else invitation.expires_at.replace(tzinfo=timezone.utc)
    if now_utc > exp:
        invitation.status = InvitationStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "This invitation link has expired. Please contact an administrator.", "error_code": "TOKEN_EXPIRED"}
        )

    return invitation


def accept_invitation(
    db: Session,
    req: InvitationAcceptRequest,
    ip_address: Optional[str] = None
) -> Tuple[User, TokenResponse]:
    # 1. Verify token
    invitation = verify_invitation_token(db, req.token)

    # 2. Strict email binding check
    req_email_clean = req.email.lower().strip()
    if invitation.email.lower().strip() != req_email_clean:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "message": f"This invitation was designated exclusively for {invitation.email}. You cannot accept it with {req_email_clean}.",
                "error_code": "EMAIL_MISMATCH"
            }
        )

    # 3. Role is strictly assigned from the verified invitation record
    assigned_role = invitation.role

    # 4. Find or create user
    user = db.query(User).filter(User.email == req_email_clean).first()
    if not user:
        user = User(
            email=req_email_clean,
            hashed_password=hash_password(req.password),
            full_name=req.full_name.strip(),
            role=assigned_role,
            phone=req.phone,
            is_active=True
        )
        db.add(user)
        db.flush()
    else:
        # User exists - update to invited role and update password if provided
        user.role = assigned_role
        user.full_name = req.full_name.strip()
        if req.phone:
            user.phone = req.phone
        if req.password:
            user.hashed_password = hash_password(req.password)

    # 5. Create associated role profile
    if assigned_role == UserRole.JUDGE:
        jp = db.query(JudgeProfile).filter(JudgeProfile.user_id == user.id).first()
        if not jp:
            jp = JudgeProfile(
                user_id=user.id,
                organization=invitation.organization or "Judge Organization",
                specialization=invitation.specialization or "Judging Panelist",
                bio=req.bio.strip() if req.bio else None
            )
            db.add(jp)
        else:
            if invitation.organization:
                jp.organization = invitation.organization
            if invitation.specialization:
                jp.specialization = invitation.specialization
            if req.bio:
                jp.bio = req.bio.strip()

    elif assigned_role == UserRole.SPONSOR:
        spp = db.query(SponsorProfile).filter(SponsorProfile.user_id == user.id).first()
        if not spp:
            spp = SponsorProfile(
                user_id=user.id,
                company_name=invitation.organization or "Partner Sponsor",
                industry=invitation.specialization or "Technology & Media",
                website=req.website.strip() if req.website else None,
                contact_phone=req.phone
            )
            db.add(spp)
        else:
            if invitation.organization:
                spp.company_name = invitation.organization
            if invitation.specialization:
                spp.industry = invitation.specialization
            if req.website:
                spp.website = req.website.strip()

    # 6. Invalidate invitation: Single-Use Sealed
    now = datetime.now(timezone.utc)
    invitation.status = InvitationStatus.ACCEPTED
    invitation.accepted_at = now
    invitation.accepted_by_id = user.id

    db.commit()
    db.refresh(user)

    log_action(
        db,
        action="INVITATION_ACCEPTED",
        entity_type="Invitation",
        entity_id=str(invitation.id),
        user_id=user.id,
        new_values={"email": user.email, "role": assigned_role.value},
        ip_address=ip_address
    )

    create_notification(
        db,
        user_id=user.id,
        title=f"Welcome to Fest Platform as {assigned_role.value}",
        message=f"Your invitation was accepted successfully! You are now authorized as a {assigned_role.value}."
    )

    # Generate JWT token
    token = create_access_token(subject=user.id, role=user.role.value, email=user.email)
    user_info = UserInfo.model_validate(user)
    token_resp = TokenResponse(access_token=token, token_type="bearer", user=user_info)

    return user, token_resp


# ==============================================================================
# WORKFLOW D: SPONSOR PARTNERSHIP APPLICATION & APPROVAL
# ==============================================================================

def apply_sponsor(
    db: Session,
    req: SponsorApplyRequest,
    ip_address: Optional[str] = None
) -> SponsorApplication:
    email_clean = req.email.lower().strip()

    existing_pending = db.query(SponsorApplication).filter(
        SponsorApplication.email == email_clean,
        SponsorApplication.status == ApplicationStatus.PENDING
    ).first()
    if existing_pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "message": "A pending Sponsor partnership application already exists for this email address.", "error_code": "APPLICATION_PENDING"}
        )

    user = db.query(User).filter(User.email == email_clean).first()
    if user:
        if user.role in [UserRole.SPONSOR, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"success": False, "message": "This account already holds Sponsor or Administrator privileges.", "error_code": "ALREADY_PRIVILEGED"}
            )
    else:
        # Create base account with STUDENT role (unprivileged until approved)
        if not req.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"success": False, "message": "Password is required to set up your sponsor partner account.", "error_code": "PASSWORD_REQUIRED"}
            )
        user = User(
            email=email_clean,
            hashed_password=hash_password(req.password),
            full_name=req.contact_name.strip(),
            role=UserRole.STUDENT,  # STRICT: Unprivileged base role
            phone=req.phone,
            is_active=True
        )
        db.add(user)
        db.flush()

    application = SponsorApplication(
        user_id=user.id,
        company_name=req.company_name.strip(),
        industry=req.industry.strip(),
        contact_name=req.contact_name.strip(),
        email=email_clean,
        phone=req.phone,
        website=req.website.strip() if req.website else None,
        proposed_tier=req.proposed_tier,
        proposal_message=req.proposal_message.strip() if req.proposal_message else None,
        status=ApplicationStatus.PENDING
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    log_action(
        db,
        action="SPONSOR_APPLICATION_SUBMITTED",
        entity_type="SponsorApplication",
        entity_id=str(application.id),
        user_id=user.id,
        new_values={"company_name": req.company_name, "email": email_clean},
        ip_address=ip_address
    )

    create_notification(
        db,
        user_id=user.id,
        title="Sponsor Proposal Submitted",
        message=f"Thank you for proposing partnership for {req.company_name}. Our fest executive committee will review your proposal shortly."
    )

    return application


def list_sponsor_applications(
    db: Session,
    status_filter: Optional[ApplicationStatus] = None
) -> List[SponsorApplication]:
    query = db.query(SponsorApplication)
    if status_filter:
        query = query.filter(SponsorApplication.status == status_filter)
    return query.order_by(SponsorApplication.created_at.desc()).all()


def approve_sponsor_application(
    db: Session,
    application_id: int,
    admin_user: User,
    admin_notes: Optional[str] = None
) -> SponsorApplication:
    application = db.query(SponsorApplication).filter(SponsorApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": "Application not found", "error_code": "NOT_FOUND"}
        )

    if application.user_id == admin_user.id or application.email == admin_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": "Administrators cannot approve their own sponsor application.", "error_code": "SELF_APPROVAL_FORBIDDEN"}
        )

    if application.status == ApplicationStatus.APPROVED:
        return application

    now = datetime.now(timezone.utc)
    application.status = ApplicationStatus.APPROVED
    application.reviewed_by_id = admin_user.id
    application.reviewed_at = now
    if admin_notes:
        application.admin_notes = admin_notes

    user = db.query(User).filter(User.id == application.user_id).first() if application.user_id else None
    if not user:
        user = db.query(User).filter(User.email == application.email).first()

    if user:
        user.role = UserRole.SPONSOR

        spp = db.query(SponsorProfile).filter(SponsorProfile.user_id == user.id).first()
        if not spp:
            spp = SponsorProfile(
                user_id=user.id,
                company_name=application.company_name,
                industry=application.industry,
                website=application.website,
                contact_phone=application.phone
            )
            db.add(spp)
        else:
            spp.company_name = application.company_name
            spp.industry = application.industry
            if application.website:
                spp.website = application.website
            if application.phone:
                spp.contact_phone = application.phone

        create_notification(
            db,
            user_id=user.id,
            title="Sponsor Partnership Approved!",
            message=f"Your partnership proposal for '{application.company_name}' has been approved! Welcome to the festival partner network."
        )

    db.commit()
    db.refresh(application)

    log_action(
        db,
        action="SPONSOR_APPLICATION_APPROVED",
        entity_type="SponsorApplication",
        entity_id=str(application.id),
        user_id=admin_user.id,
        new_values={"company": application.company_name, "email": application.email}
    )

    return application


def reject_sponsor_application(
    db: Session,
    application_id: int,
    admin_user: User,
    admin_notes: Optional[str] = None
) -> SponsorApplication:
    application = db.query(SponsorApplication).filter(SponsorApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": "Application not found", "error_code": "NOT_FOUND"}
        )

    if application.user_id == admin_user.id or application.email == admin_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": "Cannot reject your own application.", "error_code": "SELF_REJECTION_FORBIDDEN"}
        )

    now = datetime.now(timezone.utc)
    application.status = ApplicationStatus.REJECTED
    application.reviewed_by_id = admin_user.id
    application.reviewed_at = now
    if admin_notes:
        application.admin_notes = admin_notes

    if application.user_id:
        create_notification(
            db,
            user_id=application.user_id,
            title="Sponsor Application Update",
            message=f"Your partnership proposal for '{application.company_name}' was reviewed. Status: Rejected."
        )

    db.commit()
    db.refresh(application)

    log_action(
        db,
        action="SPONSOR_APPLICATION_REJECTED",
        entity_type="SponsorApplication",
        entity_id=str(application.id),
        user_id=admin_user.id,
        new_values={"company": application.company_name, "admin_notes": admin_notes}
    )

    return application
