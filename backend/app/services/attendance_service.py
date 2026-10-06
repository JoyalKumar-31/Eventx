import json
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.attendance import Attendance
from app.models.registration import Registration
from app.models.event import Event
from app.models.user import User
from app.models.enums import AttendanceStatus, RegistrationStatus
from app.services.audit_service import log_action
from app.services.notification_service import create_notification


def verify_and_record_attendance(
    db: Session,
    qr_payload: str,
    scanned_by_user_id: int,
    expected_event_id: Optional[int] = None,
    round_id: Optional[int] = None,
    remarks: Optional[str] = None
) -> Attendance:
    """
    Parses QR payload, checks registration validity, duplicate entry prevention,
    and logs attendance record.
    """
    token = qr_payload.strip()
    reg_number = None

    # Handle JSON payload or raw token/number
    if token.startswith("{"):
        try:
            data = json.loads(token)
            token = data.get("token") or token
            reg_number = data.get("reg_num")
        except Exception:
            pass

    query = db.query(Registration)
    if reg_number:
        query = query.filter(Registration.registration_number == reg_number)
    else:
        query = query.filter((Registration.qr_code_hash == token) | (Registration.registration_number == token))

    registration = query.first()
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": "Invalid QR code: Registration not found", "error_code": "INVALID_PASS"}
        )

    # Check event match if coordinator is scanning for a specific event
    if expected_event_id and registration.event_id != expected_event_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": f"Pass is for a different event (Event ID {registration.event_id})", "error_code": "EVENT_MISMATCH"}
        )

    # Check if payment is confirmed
    if registration.status == RegistrationStatus.PENDING_PAYMENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "Payment pending: Entry ticket is unconfirmed", "error_code": "PAYMENT_PENDING"}
        )

    if registration.status == RegistrationStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "Registration was cancelled", "error_code": "REGISTRATION_CANCELLED"}
        )

    # Check duplicate entry
    existing_valid_attendance = db.query(Attendance).filter(
        Attendance.registration_id == registration.id,
        Attendance.event_id == registration.event_id,
        Attendance.entry_status == AttendanceStatus.VALID
    ).first()

    if existing_valid_attendance:
        # Log duplicate entry attempt
        dup_record = Attendance(
            registration_id=registration.id,
            event_id=registration.event_id,
            round_id=round_id,
            scanned_by_user_id=scanned_by_user_id,
            scanned_at=datetime.now(timezone.utc),
            entry_status=AttendanceStatus.DUPLICATE_ATTEMPT,
            remarks=remarks or f"Duplicate entry attempt. Originally scanned at {existing_valid_attendance.scanned_at.strftime('%H:%M:%S')}"
        )
        db.add(dup_record)
        db.commit()
        db.refresh(dup_record)

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "message": f"Duplicate Entry Detected! Participant already checked in at {existing_valid_attendance.scanned_at.strftime('%Y-%m-%d %H:%M:%S')}",
                "error_code": "DUPLICATE_ENTRY",
                "participant_name": registration.user.full_name,
                "event_title": registration.event.title,
                "registration_number": registration.registration_number
            }
        )

    # First valid entry
    attendance = Attendance(
        registration_id=registration.id,
        event_id=registration.event_id,
        round_id=round_id,
        scanned_by_user_id=scanned_by_user_id,
        scanned_at=datetime.now(timezone.utc),
        entry_status=AttendanceStatus.VALID,
        remarks=remarks
    )
    db.add(attendance)

    registration.status = RegistrationStatus.ATTENDED
    db.commit()
    db.refresh(attendance)

    log_action(
        db,
        action="ATTENDANCE_RECORDED",
        entity_type="Attendance",
        entity_id=str(attendance.id),
        user_id=scanned_by_user_id,
        new_values={"registration_id": registration.id, "event_id": registration.event_id}
    )

    create_notification(
        db,
        user_id=registration.user_id,
        title="Check-In Confirmed",
        message=f"You have been successfully checked in for '{registration.event.title}'."
    )

    return attendance
