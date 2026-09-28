from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.pass_attendance import FestPass, PassStatus, Attendance, AttendanceStatus
from app.models.registration import Registration, RegistrationStatus
from app.models.event import Event
from app.models.user import User, RoleEnum
from app.schemas.pass_attendance import (
    FestPassOut, AttendanceScanResponse, CoordinatorDashboardOut, CoordinatorEventSummary
)


class AttendanceService:
    @staticmethod
    def get_pass_by_registration(db: Session, registration_id: int, current_user: User) -> FestPassOut:
        reg = db.query(Registration).options(
            joinedload(Registration.user),
            joinedload(Registration.event).joinedload(Event.venue),
            joinedload(Registration.fest_pass)
        ).filter(Registration.id == registration_id).first()

        if not reg:
            raise HTTPException(status_code=404, detail="Registration not found")

        # Allow the student themselves or coordinators/admins to view pass
        if current_user.role == RoleEnum.STUDENT and reg.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this fest pass")

        if not reg.fest_pass:
            raise HTTPException(status_code=400, detail="Fest Pass not yet generated. Payment may be pending.")

        ev = reg.event
        fest_pass = reg.fest_pass

        # Check if already checked in
        attendance_record = db.query(Attendance).filter(Attendance.registration_id == reg.id).first()
        status_label = "CHECKED_IN" if attendance_record else fest_pass.status.value

        return FestPassOut(
            id=fest_pass.id,
            registration_id=reg.id,
            participant=reg.user.full_name,
            event=ev.name,
            date=ev.event_date.strftime("%d %b %Y") if hasattr(ev.event_date, "strftime") else str(ev.event_date),
            time=ev.start_time.strftime("%I:%M %p") if hasattr(ev.start_time, "strftime") else str(ev.start_time),
            venue=ev.venue.name if ev.venue else "Campus",
            status=status_label,
            qr_token=fest_pass.qr_token,
            qr_image_url=fest_pass.qr_image_url
        )

    @staticmethod
    def get_pass_by_id(db: Session, pass_id: int, current_user: User) -> FestPassOut:
        fest_pass = db.query(FestPass).filter(FestPass.id == pass_id).first()
        if not fest_pass:
            raise HTTPException(status_code=404, detail="Fest pass not found")
        return AttendanceService.get_pass_by_registration(db, fest_pass.registration_id, current_user)

    @staticmethod
    def scan_qr(
        db: Session,
        qr_token: str,
        coordinator: User,
        expected_event_id: Optional[int] = None
    ) -> AttendanceScanResponse:
        # 1. Validate QR token
        fest_pass = db.query(FestPass).options(
            joinedload(FestPass.registration).joinedload(Registration.user),
            joinedload(FestPass.registration).joinedload(Registration.event)
        ).filter(FestPass.qr_token == qr_token.strip()).first()

        if not fest_pass:
            raise HTTPException(status_code=404, detail="Invalid QR code. Pass not recognized.")

        reg = fest_pass.registration
        if reg.status != RegistrationStatus.CONFIRMED:
            raise HTTPException(status_code=400, detail="Registration is not confirmed or payment pending")

        event = reg.event
        if expected_event_id and event.id != expected_event_id:
            raise HTTPException(
                status_code=400,
                detail=f"This pass is for '{event.name}', not the scanned event"
            )

        # 2. Check for duplicate attendance
        existing_attendance = db.query(Attendance).filter(Attendance.registration_id == reg.id).first()
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")

        if existing_attendance:
            checked_time = existing_attendance.check_in_time.strftime("%H:%M:%S")
            # Calculate current totals
            checked_count = db.query(func.count(Attendance.id)).filter(Attendance.event_id == event.id).scalar() or 0
            return AttendanceScanResponse(
                success=True,
                participant=reg.user.full_name,
                event=event.name,
                attendance="ALREADY_CHECKED_IN",
                time=checked_time,
                checked_in_count=checked_count,
                total_registered=event.registered_count,
                message=f"Participant was already checked in at {checked_time}"
            )

        # 3. Mark attendance
        attendance = Attendance(
            registration_id=reg.id,
            event_id=event.id,
            scanned_by_id=coordinator.id,
            status=AttendanceStatus.CHECKED_IN,
            check_in_time=now
        )
        db.add(attendance)
        fest_pass.status = PassStatus.USED
        db.commit()

        # 4. Get updated statistics
        checked_count = db.query(func.count(Attendance.id)).filter(Attendance.event_id == event.id).scalar() or 0

        return AttendanceScanResponse(
            success=True,
            participant=reg.user.full_name,
            event=event.name,
            attendance="CHECKED_IN",
            time=time_str,
            checked_in_count=checked_count,
            total_registered=event.registered_count,
            message=f"Successfully checked in {reg.user.full_name}"
        )

    @staticmethod
    def get_coordinator_dashboard(db: Session, coordinator: User) -> CoordinatorDashboardOut:
        # Get events assigned to this coordinator (or all active events if admin)
        query = db.query(Event).options(
            joinedload(Event.category),
            joinedload(Event.venue)
        ).filter(Event.is_active == True)

        if coordinator.role == RoleEnum.COORDINATOR:
            query = query.filter(Event.coordinator_id == coordinator.id)

        events = query.all()
        summaries = []
        total_registered_sum = 0
        total_checked_in_sum = 0

        for ev in events:
            checked_in = db.query(func.count(Attendance.id)).filter(Attendance.event_id == ev.id).scalar() or 0
            rate = round((checked_in / ev.registered_count * 100), 1) if ev.registered_count > 0 else 0.0

            total_registered_sum += ev.registered_count
            total_checked_in_sum += checked_in

            summaries.append(
                CoordinatorEventSummary(
                    id=ev.id,
                    name=ev.name,
                    category=ev.category.name if ev.category else "General",
                    event_date=str(ev.event_date),
                    time=f"{ev.start_time.strftime('%I:%M %p')} - {ev.end_time.strftime('%I:%M %p')}",
                    venue=ev.venue.name if ev.venue else "Campus",
                    registered_count=ev.registered_count,
                    checked_in_count=checked_in,
                    attendance_rate=rate
                )
            )

        overall_rate = round((total_checked_in_sum / total_registered_sum * 100), 1) if total_registered_sum > 0 else 0.0

        return CoordinatorDashboardOut(
            coordinator_name=coordinator.full_name,
            assigned_events=summaries,
            total_registered=total_registered_sum,
            total_checked_in=total_checked_in_sum,
            overall_attendance_rate=overall_rate
        )

    @staticmethod
    def get_event_attendance_list(db: Session, event_id: int):
        records = db.query(Attendance).options(
            joinedload(Attendance.registration).joinedload(Registration.user)
        ).filter(Attendance.event_id == event_id).order_by(Attendance.check_in_time.desc()).all()

        return [
            {
                "registration_id": a.registration_id,
                "participant_name": a.registration.user.full_name,
                "email": a.registration.user.email,
                "college": a.registration.user.college,
                "check_in_time": a.check_in_time.strftime("%I:%M:%S %p"),
                "status": a.status.value
            }
            for a in records
        ]
