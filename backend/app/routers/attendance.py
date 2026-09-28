from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.user import User, RoleEnum
from app.schemas.pass_attendance import AttendanceScanRequest, AttendanceScanResponse
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance & QR Verification"])


@router.post("/scan", response_model=AttendanceScanResponse)
def scan_attendance_qr(
    scan_req: AttendanceScanRequest,
    current_user: User = Depends(require_role(RoleEnum.COORDINATOR, RoleEnum.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    QR verification endpoint for event coordinators.
    Validates pass, verifies event, prevents duplicate entry, marks check-in,
    and returns live event attendance count.
    """
    return AttendanceService.scan_qr(
        db=db,
        qr_token=scan_req.qr_token,
        coordinator=current_user,
        expected_event_id=scan_req.event_id
    )
