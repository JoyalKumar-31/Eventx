from fastapi import APIRouter, Depends, Request, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.application import (
    InvitationVerifyResponse,
    InvitationAcceptRequest,
)
from app.schemas.auth import TokenResponse
from app.services.application_service import verify_invitation_token, accept_invitation

router = APIRouter(prefix="/invitations", tags=["Invitations"])


@router.get("/verify", response_model=InvitationVerifyResponse)
def verify_invitation(
    token: str = Query(..., description="The invitation token provided by the administrator"),
    db: Session = Depends(get_db)
):
    """
    Publicly verifies an invitation token.
    Returns invitation role, designated email, and organization without revealing private data.
    """
    inv = verify_invitation_token(db=db, raw_token=token)
    return InvitationVerifyResponse(
        valid=True,
        email=inv.email,
        role=inv.role,
        organization=inv.organization,
        specialization=inv.specialization,
        expires_at=inv.expires_at
    )


@router.post("/accept", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def accept_single_use_invitation(
    req: InvitationAcceptRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Accepts an administrator-issued single-use invitation.
    Binds the account to the invited email, grants the invited role (Judge or Sponsor),
    invalidates the token forever, and returns an authenticated JWT session.
    """
    client_ip = request.client.host if request.client else None
    user, token_resp = accept_invitation(db=db, req=req, ip_address=client_ip)
    return token_resp
