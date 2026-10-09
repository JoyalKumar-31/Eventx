from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.enums import UserRole, AttendanceStatus
from app.models.event import Event
from app.models.registration import Registration
from app.models.attendance import Attendance
from app.models.user import User
from app.schemas.attendance import QRScanRequest, AttendanceResponse, AttendanceStats
from app.services.attendance_service import verify_and_record_attendance

router = APIRouter(prefix="/attendance", tags=["Attendance"])


def format_att_response(att: Attendance) -> AttendanceResponse:
    part_name = att.registration.user.full_name if (att.registration and att.registration.user) else "Participant"
    part_email = att.registration.user.email if (att.registration and att.registration.user) else ""
    reg_obj = {
        "id": att.registration_id,
        "registration_number": att.registration.registration_number if att.registration else None,
        "user": {
            "id": att.registration.user.id if (att.registration and att.registration.user) else None,
            "full_name": part_name,
            "email": part_email
        } if (att.registration and att.registration.user) else None
    }
    return AttendanceResponse(
        id=att.id,
        registration_id=att.registration_id,
        event_id=att.event_id,
        participant_name=part_name,
        participant_email=part_email,
        event_title=att.event.title if att.event else f"Event #{att.event_id}",
        entry_status=att.entry_status,
        scanned_at=att.scanned_at,
        remarks=att.remarks,
        registration=reg_obj
    )


@router.post("/scan", response_model=AttendanceResponse, status_code=status.HTTP_200_OK)
def scan_qr_entry_pass(
    req: QRScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    """
    Validates QR entry ticket for participant.
    Prevents duplicate entries, checks event match, and marks attendance.
    """
    payload = req.qr_payload or req.qr_hash
    attendance = verify_and_record_attendance(
        db=db,
        qr_payload=payload,
        scanned_by_user_id=current_user.id,
        expected_event_id=req.event_id,
        round_id=req.round_id,
        remarks=req.remarks
    )
    return format_att_response(attendance)


@router.get("/event/{event_id}", response_model=List[AttendanceResponse])
def get_event_attendance(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    records = db.query(Attendance).filter(Attendance.event_id == event_id).order_by(Attendance.scanned_at.desc()).all()
    return [format_att_response(r) for r in records]


@router.get("/stats/{event_id}", response_model=AttendanceStats)
def get_event_attendance_stats(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    total_reg = db.query(Registration).filter(Registration.event_id == event_id).count()
    total_att = db.query(Attendance).filter(
        Attendance.event_id == event_id,
        Attendance.entry_status == AttendanceStatus.VALID
    ).count()

    pct = round((total_att / total_reg * 100), 1) if total_reg > 0 else 0.0

    return AttendanceStats(
        total_registrations=total_reg,
        total_attended=total_att,
        attendance_percentage=pct
    )
