"""
tools/event_tools.py - Event Management and Scheduling Tools
Integrated with live MySQL database and fallback dataset.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional


def get_all_events() -> List[Dict[str, Any]]:
    """Returns a list of all registered fest events directly from the database."""
    try:
        from app.db.session import SessionLocal
        from app.models.event import Event
        from app.models.enums import EventStatus
        db = SessionLocal()
        try:
            db_events = (
                db.query(Event)
                .filter(Event.status != EventStatus.DRAFT)
                .order_by(Event.created_at.desc(), Event.id.desc())
                .all()
            )
            summary = []
            for ev in db_events:
                start_str = ev.start_time.strftime("%d %b, %I:%M %p") if ev.start_time else "TBA"
                end_str = ev.end_time.strftime("%d %b, %I:%M %p") if ev.end_time else "TBA"
                venue_str = ev.venue.name if ev.venue else "Campus Arena"
                if ev.venue and ev.venue.room_number:
                    venue_str += f" ({ev.venue.room_number})"
                now = datetime.now()
                is_full = ev.current_participants >= ev.max_participants
                is_deadline_passed = bool(ev.registration_deadline and ev.registration_deadline < now)
                ev_status_val = str(ev.status.value if hasattr(ev.status, "value") else ev.status).upper()
                is_completed = bool(ev.end_time and ev.end_time < now) or (ev_status_val == "COMPLETED")
                summary.append({
                    "event_key": str(ev.id),
                    "id": ev.id,
                    "coordinator_id": ev.coordinator_id,
                    "title": ev.title,
                    "status": ev_status_val,
                    "category": ev.category.name if ev.category else "General",
                    "venue": venue_str,
                    "time": f"{start_str} - {end_str}",
                    "team_size": f"{ev.min_team_size}-{ev.max_team_size} members" if ev.is_team_event else "Individual (Solo)",
                    "fee": f"Rs. {float(ev.registration_fee):.0f}" if ev.registration_fee > 0 else "Free Entry",
                    "registration_deadline": ev.registration_deadline.strftime("%d %b, %I:%M %p") if ev.registration_deadline else "TBA",
                    "current_participants": ev.current_participants,
                    "max_participants": ev.max_participants,
                    "is_capacity_full": is_full,
                    "is_deadline_passed": is_deadline_passed,
                    "is_completed": is_completed,
                    "participants": f"{ev.current_participants}/{ev.max_participants}",
                    "created_at": ev.created_at.strftime("%Y-%m-%d %H:%M:%S") if ev.created_at else None
                })
            return summary
        finally:
            db.close()
    except Exception:
        return []


def get_event_details(event_name: str) -> Optional[Dict[str, Any]]:
    """
    Search and return full details and rules for a given event name or keyword.
    """
    import re
    try:
        from app.db.session import SessionLocal
        from app.models.event import Event
        from app.models.enums import EventStatus
        db = SessionLocal()
        try:
            clean = event_name.lower().strip()
            db_events = (
                db.query(Event)
                .filter(Event.status != EventStatus.DRAFT)
                .order_by(Event.created_at.desc(), Event.id.desc())
                .all()
            )

            # 1. Exact or substring match of event title
            for ev in db_events:
                ev_name_lower = ev.title.lower()
                if ev_name_lower == clean or ev_name_lower in clean or clean in ev_name_lower:
                    rules = [r.description for r in ev.rules] if ev.rules else [
                        "All submissions must be original work.",
                        "Participants must adhere to the campus festival code of conduct."
                    ]
                    start_str = ev.start_time.strftime("%d %b, %I:%M %p") if ev.start_time else "TBA"
                    end_str = ev.end_time.strftime("%d %b, %I:%M %p") if ev.end_time else "TBA"
                    venue_str = ev.venue.name if ev.venue else "Campus Arena"
                    if ev.venue and ev.venue.room_number:
                        venue_str += f" ({ev.venue.room_number})"
                    is_full = ev.current_participants >= ev.max_participants
                    return {
                        "id": ev.id,
                        "coordinator_id": ev.coordinator_id,
                        "title": ev.title,
                        "status": ev.status.value if hasattr(ev.status, "value") else str(ev.status),
                        "category": ev.category.name if ev.category else "General",
                        "venue": venue_str,
                        "start_time": start_str,
                        "end_time": end_str,
                        "min_team_size": ev.min_team_size,
                        "max_team_size": ev.max_team_size,
                        "is_team_event": ev.is_team_event,
                        "registration_fee": float(ev.registration_fee),
                        "current_participants": ev.current_participants,
                        "max_participants": ev.max_participants,
                        "is_capacity_full": is_full,
                        "rules": rules
                    }

            # 2. Token match excluding common query stopwords
            stopwords = {
                "what", "are", "the", "for", "and", "rules", "rule", "detail", "details",
                "when", "where", "about", "show", "tell", "give", "info", "information",
                "event", "events", "how", "much", "many", "does", "cost", "new", "latest",
                "recent", "recently", "added", "update", "updated", "which", "list", "all",
                "available", "happening", "upcoming", "can", "see", "view", "display"
            }
            words = [w for w in re.findall(r'[a-zA-Z0-9]+', clean) if len(w) > 2 and w not in stopwords]
            
            best_match = None
            max_matches = 0
            for ev in db_events:
                ev_tokens = set(re.findall(r'[a-zA-Z0-9]+', ev.title.lower()))
                matches = sum(1 for w in words if w in ev_tokens or any(w in t for t in ev_tokens))
                if matches > max_matches:
                    max_matches = matches
                    best_match = ev

            if best_match and max_matches > 0:
                rules = [r.description for r in best_match.rules] if best_match.rules else [
                    "All submissions must be original work.",
                    "Participants must adhere to the campus festival code of conduct."
                ]
                start_str = best_match.start_time.strftime("%d %b, %I:%M %p") if best_match.start_time else "TBA"
                end_str = best_match.end_time.strftime("%d %b, %I:%M %p") if best_match.end_time else "TBA"
                venue_str = best_match.venue.name if best_match.venue else "Campus Arena"
                if best_match.venue and best_match.venue.room_number:
                    venue_str += f" ({best_match.venue.room_number})"
                is_full = best_match.current_participants >= best_match.max_participants
                return {
                    "id": best_match.id,
                    "coordinator_id": best_match.coordinator_id,
                    "title": best_match.title,
                    "status": best_match.status.value if hasattr(best_match.status, "value") else str(best_match.status),
                    "category": best_match.category.name if best_match.category else "General",
                    "venue": venue_str,
                    "start_time": start_str,
                    "end_time": end_str,
                    "min_team_size": best_match.min_team_size,
                    "max_team_size": best_match.max_team_size,
                    "is_team_event": best_match.is_team_event,
                    "registration_fee": float(best_match.registration_fee),
                    "current_participants": best_match.current_participants,
                    "max_participants": best_match.max_participants,
                    "is_capacity_full": is_full,
                    "rules": rules
                }
        finally:
            db.close()
    except Exception:
        pass

    return None


def check_schedule_clash(event1_name: str, event2_name: str) -> Dict[str, Any]:
    """
    Checks if two events clash in time or venue.
    """
    e1 = get_event_details(event1_name)
    e2 = get_event_details(event2_name)
    
    if not e1 or not e2:
        return {"clash": False, "reason": "One or both events could not be found."}
    
    venue_clash = (e1["venue"].lower() == e2["venue"].lower())
    time_clash = (e1["start_time"] == e2["start_time"])
    
    return {
        "event_1": e1["title"],
        "event_2": e2["title"],
        "venue_clash": venue_clash,
        "time_clash": time_clash,
        "has_conflict": venue_clash or time_clash,
        "details": f"{e1['title']} ({e1['start_time']} at {e1['venue']}) vs {e2['title']} ({e2['start_time']} at {e2['venue']})"
    }


def get_coordinator_created_events(coordinator_id: Optional[int] = None, user_email: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns all events created and coordinated by the specified coordinator with real-time registration capacity counts.
    """
    try:
        from app.db.session import SessionLocal
        from app.models.event import Event
        from app.models.user import User
        from app.models.enums import EventStatus, UserRole

        db = SessionLocal()
        try:
            user = None
            if coordinator_id:
                try:
                    user = db.query(User).filter(User.id == int(coordinator_id)).first()
                except Exception:
                    pass
            if not user and user_email:
                user = db.query(User).filter(User.email == user_email.strip().lower()).first()

            if not user:
                return {
                    "success": False,
                    "error": "USER_NOT_FOUND",
                    "message": "⚠️ Coordinator account not found. Please log in with your event coordinator account to view managed events."
                }

            events = (
                db.query(Event)
                .filter(Event.coordinator_id == user.id)
                .order_by(Event.created_at.desc(), Event.id.desc())
                .all()
            )

            if not events:
                return {
                    "success": True,
                    "coordinator_id": user.id,
                    "coordinator_name": user.full_name,
                    "events": [],
                    "message": (
                        f"### 📋 Events Managed by {user.full_name}\n\n"
                        f"You have not created any festival competitions or workshops yet.\n\n"
                        f"👉 Launch your first event in the [Coordinator Events Portal](/coordinator/events) or access your [Coordinator Dashboard](/coordinator/dashboard)!"
                    )
                }

            lines = []
            for ev in events:
                start_str = ev.start_time.strftime("%d %b, %I:%M %p") if ev.start_time else "TBA"
                end_str = ev.end_time.strftime("%d %b, %I:%M %p") if ev.end_time else "TBA"
                venue_str = ev.venue.name if ev.venue else "Campus Arena"
                if ev.venue and ev.venue.room_number:
                    venue_str += f" ({ev.venue.room_number})"

                is_full = ev.current_participants >= ev.max_participants
                spots_left = max(0, ev.max_participants - ev.current_participants)
                status_val = ev.status.value if hasattr(ev.status, "value") else str(ev.status)
                fee_str = f"Rs. {float(ev.registration_fee):.0f}" if ev.registration_fee > 0 else "Free Entry"

                if is_full:
                    capacity_str = f"🔴 **CAPACITY FULL** (`{ev.current_participants}/{ev.max_participants}` registered)"
                else:
                    capacity_str = f"🟢 **{ev.current_participants}/{ev.max_participants} spots filled** (`{spots_left}` remaining)"

                lines.append(
                    f"• **{ev.title}** ({ev.category.name if ev.category else 'General'}) — `[{status_val}]`\n"
                    f"  - ⏰ **Schedule**: {start_str} – {end_str}\n"
                    f"  - 📍 **Venue**: {venue_str}\n"
                    f"  - 👥 **Registrations**: {capacity_str}\n"
                    f"  - 💰 **Entry Fee**: {fee_str} | **Team**: {'Team' if ev.is_team_event else 'Solo'}\n"
                    f"  - 🔗 [View Registrations](/coordinator/registrations) | [Edit Event](/coordinator/events)"
                )

            events_msg = (
                f"### 📋 Events Created & Coordinated by **{user.full_name}**\n\n"
                f"You are currently managing **{len(events)}** festival competition(s):\n\n"
                + "\n\n".join(lines)
                + f"\n\n💡 *Ask: 'How many are registered for [Event Name]?' to view real-time attendee rosters and check-in statuses!*"
            )

            return {
                "success": True,
                "coordinator_id": user.id,
                "coordinator_name": user.full_name,
                "events_count": len(events),
                "message": events_msg
            }
        finally:
            db.close()
    except Exception as exc:
        return {
            "success": False,
            "error": "DB_ERROR",
            "message": f"Could not retrieve coordinator events due to an error: {str(exc)}"
        }


def get_event_registrations_summary(event_name_or_id: str, coordinator_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Returns registration count, capacity status, and roster breakdown for a specific event.
    """
    import re
    try:
        from app.db.session import SessionLocal
        from app.models.event import Event
        from app.models.registration import Registration
        from app.models.enums import RegistrationStatus, EventStatus

        db = SessionLocal()
        try:
            clean = str(event_name_or_id).lower().strip()
            # Clean common question prefix/suffix phrases
            clean_cleaned = re.sub(r'\b(how|many|are|registrations?|registered|for|in|who|tell|me|show|check|the|event|participants?|count|status)\b', ' ', clean).strip()

            target_event = None
            if clean_cleaned.isdigit():
                target_event = db.query(Event).filter(Event.id == int(clean_cleaned)).first()
            elif clean.isdigit():
                target_event = db.query(Event).filter(Event.id == int(clean)).first()

            all_db_events = db.query(Event).order_by(Event.created_at.desc(), Event.id.desc()).all()

            if not target_event:
                # 1. Exact or substring match
                for ev in all_db_events:
                    ev_lower = ev.title.lower()
                    if clean_cleaned and (clean_cleaned == ev_lower or clean_cleaned in ev_lower or ev_lower in clean_cleaned):
                        target_event = ev
                        break

            if not target_event:
                # 2. Token match
                tokens = [w for w in clean_cleaned.split() if len(w) > 2]
                for ev in all_db_events:
                    ev_lower = ev.title.lower()
                    if any(t in ev_lower for t in tokens):
                        target_event = ev
                        break

            if not target_event:
                avail = ", ".join(f"**{e.title}**" for e in all_db_events[:6])
                return {
                    "success": False,
                    "error": "EVENT_NOT_FOUND",
                    "message": (
                        f"Could not find an event matching '{event_name_or_id}'.\n\n"
                        f"Active events in festival catalog: {avail}.\n"
                        f"Please ask: *'How many are registered for [Event Name]'*."
                    )
                }

            # Query all registrations for this event
            regs = (
                db.query(Registration)
                .filter(Registration.event_id == target_event.id)
                .order_by(Registration.registered_at.desc())
                .all()
            )

            total_regs = len(regs)
            confirmed_cnt = sum(1 for r in regs if r.status == RegistrationStatus.CONFIRMED)
            attended_cnt = sum(1 for r in regs if r.status == RegistrationStatus.ATTENDED)
            pending_cnt = sum(1 for r in regs if r.status == RegistrationStatus.PENDING_PAYMENT)
            cancelled_cnt = sum(1 for r in regs if r.status == RegistrationStatus.CANCELLED)

            max_cap = target_event.max_participants
            current_participants = target_event.current_participants
            # Fallback to total_regs if counter differs
            effective_cnt = max(current_participants, confirmed_cnt + attended_cnt)
            is_full = effective_cnt >= max_cap
            spots_left = max(0, max_cap - effective_cnt)

            venue_str = target_event.venue.name if target_event.venue else "Campus Arena"
            start_str = target_event.start_time.strftime("%d %b, %I:%M %p") if target_event.start_time else "TBA"
            end_str = target_event.end_time.strftime("%d %b, %I:%M %p") if target_event.end_time else "TBA"

            if is_full:
                cap_badge = f"🔴 **CAPACITY FULL** ({effective_cnt}/{max_cap})"
                student_notice = "⚠️ **Notice**: This event has reached maximum capacity. New registrations are marked as full."
            else:
                cap_badge = f"🟢 **OPEN** ({effective_cnt}/{max_cap} spots filled, **{spots_left}** spots remaining)"
                student_notice = f"✅ **Notice**: Registrations are open. {spots_left} open spot(s) remaining."

            # Roster preview
            roster_lines = []
            for r in regs[:6]:
                user_label = r.user.full_name if r.user else "Anonymous"
                team_label = f"Team: {r.team.name}" if r.team else "Solo"
                status_tag = f"`{r.status.value if hasattr(r.status, 'value') else str(r.status)}`"
                roster_lines.append(f"• `{r.registration_number}` — **{user_label}** ({team_label}) — {status_tag}")

            roster_str = "\n".join(roster_lines) if roster_lines else "• *No participants have registered yet.*"

            summary_msg = (
                f"### 📊 Registration & Capacity Report: **{target_event.title}**\n\n"
                f"📍 **Venue**: {venue_str} | ⏰ **Time**: {start_str} – {end_str}\n"
                f"👥 **Capacity Status**: {cap_badge}\n\n"
                f"📈 **Live Breakdown**:\n"
                f"• **Total Registrations**: **{total_regs}**\n"
                f"• **Confirmed Active**: `{confirmed_cnt}`\n"
                f"• **Attended / Present**: `{attended_cnt}`\n"
                f"• **Pending Payment**: `{pending_cnt}`\n"
                f"• **Available Spots**: **{spots_left}** / {max_cap}\n\n"
                f"{student_notice}\n\n"
                f"📋 **Recent Registered Attendees**:\n"
                f"{roster_str}\n\n"
                f"🔗 Manage attendance and registrations in the [Coordinator Registrations Portal](/coordinator/registrations)."
            )

            return {
                "success": True,
                "event_id": target_event.id,
                "event_title": target_event.title,
                "current_participants": effective_cnt,
                "max_participants": max_cap,
                "is_full": is_full,
                "spots_left": spots_left,
                "total_registrations": total_regs,
                "confirmed": confirmed_cnt,
                "attended": attended_cnt,
                "pending": pending_cnt,
                "message": summary_msg
            }
        finally:
            db.close()
    except Exception as exc:
        return {
            "success": False,
            "error": "DB_ERROR",
            "message": f"Could not inspect event registrations: {str(exc)}"
        }
