import re
import json
import secrets
from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple, Any, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from app.models.event import Event, EventCategory, ScheduleItem, Venue
from app.models.registration import Registration
from app.models.user import User
from app.models.ai import AIConversation, AIMessage
from app.schemas.ai import AIChatResponse, AIActionOut, AgentQueryResponse, AgentInfoOut

# Import LangGraph multi-agent application
from fest_agents.graph import app as fest_graph


class AIService:
    @staticmethod
    def get_agents_info() -> List[AgentInfoOut]:
        """
        Returns metadata and capabilities for all 7 fest management AI agents.
        """
        return [
            AgentInfoOut(
                name="Supervisor Agent",
                agent_id="supervisor",
                role_title="Multi-Agent Coordinator & Intent Classifier",
                description="Analyzes incoming requests and dynamically routes to the appropriate specialist agent.",
                capabilities=["Intent classification", "Role-based dispatching", "Workflow coordination"]
            ),
            AgentInfoOut(
                name="Event Management Agent",
                agent_id="event_agent",
                role_title="Event Catalog & Schedule Specialist",
                description="Queries live fest events, venues, timings, rules, and detects scheduling conflicts.",
                capabilities=["Event catalog search", "Venue navigation", "Rule explanations", "Schedule clash detection"]
            ),
            AgentInfoOut(
                name="Participant & Team Agent",
                agent_id="participant_agent",
                role_title="Registration & Access Control Specialist",
                description="Validates team size rules, checks participant registration status, and inspects QR gate passes.",
                capabilities=["Team size validation", "Registration lookup", "QR pass verification", "Gate entry tracking"]
            ),
            AgentInfoOut(
                name="Judging & Evaluation Agent",
                agent_id="judging_agent",
                role_title="Scoring, Rubrics & Leaderboard Specialist",
                description="Assists judges with category rubrics, calculates weighted marks, and computes verified rankings.",
                capabilities=["Judging rubrics", "Live standings computation", "Leaderboard generation"]
            ),
            AgentInfoOut(
                name="Result & Certificate Agent",
                agent_id="result_cert_agent",
                role_title="Winner Announcements & Certificate Specialist",
                description="Generates publication-ready winner announcements and tamper-proof certificate verification text.",
                capabilities=["Winner announcements", "Certificate text generation", "Verification IDs"]
            ),
            AgentInfoOut(
                name="Sponsor & Analytics Agent",
                agent_id="sponsor_analytics_agent",
                role_title="Fest Statistics & Partner Operations Specialist",
                description="Aggregates live participant footfall, event counts, ticket revenue, and corporate sponsor reports.",
                capabilities=["Live revenue tracking", "Footfall analytics", "Sponsor tier reports", "Gate check-in rates"]
            ),
            AgentInfoOut(
                name="General FAQ & Helpdesk Agent",
                agent_id="faq_agent",
                role_title="Campus Guide & Support Specialist",
                description="Provides instant answers regarding campus navigation, registration counters, and payment policies.",
                capabilities=["Campus directions", "UPI verification help", "Lost & Found info", "Desk locations"]
            )
        ]

    @staticmethod
    def execute_agent_workflow(
        question: str,
        role: str = "student",
        event_context: Optional[dict] = None
    ) -> AgentQueryResponse:
        """
        Direct invocation of the LangGraph multi-agent workflow (compatible with teammate's spec).
        """
        result = fest_graph.invoke({
            "question": question,
            "user_role": role,
            "history": [],
            "attempts": 0,
            "event_context": event_context or {}
        })

        return AgentQueryResponse(
            response=result.get("agent_response", ""),
            route_taken=result.get("route", "faq_agent"),
            trace=result.get("history", []),
            tool_outputs=result.get("tool_outputs")
        )

    @staticmethod
    def process_message(
        db: Session,
        message: str,
        user: Optional[User] = None,
        session_id: Optional[str] = None
    ) -> AIChatResponse:
        """
        FEST AI conversational endpoint for the React frontend.
        Combines LangGraph multi-agent workflow with structured Action Cards and persistence.
        """
        current_session = session_id or f"sess_{secrets.token_hex(8)}"
        clean_msg = message.strip()
        lower_msg = clean_msg.lower()

        # 1. Retrieve or create conversation record in DB
        conv = db.query(AIConversation).filter(AIConversation.session_id == current_session).first()
        if not conv:
            conv = AIConversation(
                user_id=user.id if user else None,
                session_id=current_session,
                title=clean_msg[:40]
            )
            db.add(conv)
            db.commit()
            db.refresh(conv)

        # Record user message in DB
        user_msg_record = AIMessage(
            conversation_id=conv.id,
            sender="user",
            content=clean_msg,
            message_type="text"
        )
        db.add(user_msg_record)

        # 2. Invoke LangGraph multi-agent system
        user_role_str = user.role.value.lower() if (user and hasattr(user, 'role') and user.role) else "student"
        graph_output = fest_graph.invoke({
            "question": clean_msg,
            "user_role": user_role_str,
            "history": [],
            "attempts": 0,
            "event_context": {}
        })

        route = graph_output.get("route", "faq_agent")
        bot_message = graph_output.get("agent_response", "")
        tool_outputs = graph_output.get("tool_outputs") or {}

        # 3. Derive structured data and action cards for React Frontend
        response_type = "text"
        structured_data = None
        actions: List[AIActionOut] = []

        # --- ROUTE: EVENT AGENT ---
        if route == "event_agent":
            # Search if a specific event was queried or listed
            all_active = db.query(Event).options(
                joinedload(Event.venue),
                joinedload(Event.category)
            ).filter(Event.is_active == True).all()

            matched_event = None
            for ev in all_active:
                if ev.name.lower() in lower_msg or str(ev.id) in lower_msg:
                    matched_event = ev
                    break
            
            if matched_event:
                response_type = "action_card"
                structured_data = {
                    "id": matched_event.id,
                    "name": matched_event.name,
                    "venue": matched_event.venue.name if matched_event.venue else "Campus",
                    "fee": float(matched_event.registration_fee),
                    "team_size": f"{matched_event.min_team_size}-{matched_event.max_team_size}"
                }
                actions.append(AIActionOut(
                    type="VIEW_EVENT",
                    event_id=matched_event.id,
                    label=f"View {matched_event.name}"
                ))
                actions.append(AIActionOut(
                    type="REGISTER_EVENT",
                    event_id=matched_event.id,
                    label=f"Register for {matched_event.name}"
                ))
            elif any(w in lower_msg for w in ["schedule", "timing", "when", "agenda", "timeline"]):
                response_type = "schedule_list"
                schedules = db.query(ScheduleItem).options(
                    joinedload(ScheduleItem.venue),
                    joinedload(ScheduleItem.event)
                ).order_by(ScheduleItem.date.asc(), ScheduleItem.start_time.asc()).limit(5).all()
                structured_data = [
                    {
                        "id": s.id,
                        "title": s.title,
                        "date": str(s.date),
                        "time": f"{s.start_time.strftime('%I:%M %p')} - {s.end_time.strftime('%I:%M %p')}",
                        "venue": s.venue.name if s.venue else "Campus",
                        "category": s.category or "General"
                    }
                    for s in schedules
                ]
                actions.append(AIActionOut(type="VIEW_SCHEDULE", label="View Full Fest Timeline", url="/schedule"))
            else:
                events_to_show = all_active
                if "tech" in lower_msg:
                    events_to_show = [e for e in all_active if e.category and "tech" in e.category.name.lower()] or all_active
                elif "cult" in lower_msg:
                    events_to_show = [e for e in all_active if e.category and "cult" in e.category.name.lower()] or all_active

                response_type = "event_list"
                structured_data = [
                    {
                        "id": ev.id,
                        "name": ev.name,
                        "time": ev.start_time.strftime("%I:%M %p"),
                        "date": str(ev.event_date),
                        "venue": ev.venue.name if ev.venue else "Campus",
                        "registration_fee": float(ev.registration_fee)
                    }
                    for ev in events_to_show[:4]
                ]
                for ev in events_to_show[:4]:
                    actions.append(AIActionOut(
                        type="VIEW_EVENT",
                        event_id=ev.id,
                        label=f"View {ev.name}"
                    ))
                actions.append(AIActionOut(type="EXPLORE_EVENTS", label="Explore All Events", url="/events"))
                actions.append(AIActionOut(type="VIEW_SCHEDULE", label="View Schedule Timeline", url="/schedule"))

        # --- ROUTE: PARTICIPANT & TEAM AGENT ---
        elif route == "participant_agent":
            if user:
                regs = db.query(Registration).filter(Registration.user_id == user.id).all()
                if regs:
                    response_type = "registration_info"
                    structured_data = [
                        {
                            "registration_id": r.id,
                            "event_name": r.event.name if r.event else "Event",
                            "status": r.status.value,
                            "has_pass": r.fest_pass is not None
                        }
                        for r in regs
                    ]
                    for r in regs:
                        if r.fest_pass:
                            actions.append(AIActionOut(
                                type="VIEW_PASS",
                                event_id=r.event_id,
                                label=f"Show Pass: {r.event.name if r.event else 'Pass'}",
                                url=f"/passes/{r.id}"
                            ))
                else:
                    actions.append(AIActionOut(type="EXPLORE_EVENTS", label="Browse Competitions", url="/events"))
            else:
                actions.append(AIActionOut(type="LOGIN", label="Login to Check Passes", url="/login"))

        # --- ROUTE: JUDGING AGENT ---
        elif route == "judging_agent":
            response_type = "action_card"
            actions.append(AIActionOut(type="VIEW_LEADERBOARD", label="View Official Leaderboard", url="/results"))
            if user and user_role_str in ["judge", "admin", "coordinator"]:
                actions.append(AIActionOut(type="JUDGING_PANEL", label="Open Judging Portal", url="/judging"))

        # --- ROUTE: RESULT & CERTIFICATE AGENT ---
        elif route == "result_cert_agent":
            response_type = "action_card"
            actions.append(AIActionOut(type="VIEW_RESULTS", label="View Event Results", url="/results"))
            if user:
                actions.append(AIActionOut(type="VIEW_CERTIFICATES", label="My Certificates", url="/certificates"))

        # --- ROUTE: SPONSOR & ANALYTICS AGENT ---
        elif route == "sponsor_analytics_agent":
            response_type = "action_card"
            actions.append(AIActionOut(type="VIEW_ANALYTICS", label="Fest Dashboard Analytics", url="/analytics"))
            actions.append(AIActionOut(type="VIEW_SPONSORS", label="Sponsor Partners", url="/sponsors"))

        # --- ROUTE: FAQ & HELPDESK AGENT ---
        else:
            actions.append(AIActionOut(type="EXPLORE_EVENTS", label="Explore Events", url="/events"))
            actions.append(AIActionOut(type="VIEW_SCHEDULE", label="Check Timeline", url="/schedule"))

        # 4. Save assistant response in MySQL history
        assistant_msg_record = AIMessage(
            conversation_id=conv.id,
            sender="assistant",
            content=bot_message,
            message_type=response_type,
            structured_data=json.dumps(structured_data) if structured_data else None
        )
        db.add(assistant_msg_record)
        db.commit()

        return AIChatResponse(
            message=bot_message,
            type=response_type,
            data=structured_data,
            actions=actions,
            session_id=current_session
        )
