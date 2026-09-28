"""
nodes.py - Agent nodes for College Fest Management System using Groq API (Llama 3.3 70B)
with automatic offline/fallback intelligence.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from .state import AgentState
from .tools import (
    get_all_events,
    get_event_details,
    check_schedule_clash,
    validate_team_size,
    check_registration_status,
    verify_qr_entry_pass,
    get_evaluation_rubric,
    calculate_rankings,
    get_live_event_results,
    get_fest_analytics,
    get_sponsor_reports,
    generate_certificate_text,
    draft_announcement
)

# Load environment variables
load_dotenv()

# Initialize Groq LLM lazily / safely
_llm_instance = None


def get_llm():
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key and not groq_api_key.startswith("gsk_your_groq_api_key") and len(groq_api_key) > 10:
        try:
            from langchain_groq import ChatGroq
            _llm_instance = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.2,
                api_key=groq_api_key
            )
            return _llm_instance
        except Exception:
            return None
    return None


def invoke_llm(prompt: str, agent_type: str, state: AgentState) -> str:
    """
    Invokes Groq Llama 3.3 70B if available.
    If Groq API key is not configured or network error occurs,
    uses high-quality rule/tool-based response generation.
    """
    llm = get_llm()
    if llm:
        try:
            response = llm.invoke(prompt)
            content = response.content.strip()
            if content.startswith("```"):
                content = content.strip("`").strip()
            return content
        except Exception:
            pass

    # High-quality fallback generation
    return _generate_fallback(agent_type, state)


def _generate_fallback(agent_type: str, state: AgentState) -> str:
    question = state.get("question", "")
    lower = question.lower()
    role = state.get("user_role", "student")

    if agent_type == "supervisor":
        import re
        tokens = set(re.findall(r'[a-zA-Z0-9_-]+', lower))
        
        def has_any(keywords):
            for k in keywords:
                if " " in k:
                    if k in lower:
                        return True
                else:
                    if k in tokens or any(t.startswith(k) for t in tokens):
                        return True
            return False

        if has_any(["cert", "certificate", "certificates", "winner", "winners", "announc"]):
            return "result_cert_agent"
        elif has_any(["judge", "judges", "judging", "rubric", "evaluat", "rank", "ranking", "rankings", "leaderboard"]):
            return "judging_agent"
        elif has_any(["sponsor", "sponsors", "analytic", "analytics", "revenue", "footfall", "financial", "funding", "stats", "statistics"]):
            return "sponsor_analytics_agent"
        elif has_any(["reg-", "pass-", "qr", "gate", "attendance", "checkin", "check-in"]):
            return "participant_agent"
        elif has_any(["timing", "timings", "venue", "schedule", "schedules", "clash", "rules", "when", "hackathon", "codesprint", "bytehack"]):
            return "event_agent"
        elif has_any(["member", "members", "team", "teams", "register", "registration", "registrations", "participant"]):
            return "participant_agent"
        elif has_any(["event", "events"]):
            return "event_agent"
        else:
            return "faq_agent"

    elif agent_type == "event_agent":
        matched = get_event_details(question)
        if matched:
            rules_str = "\n".join(f"• {r}" for r in matched.get("rules", []))
            return (
                f"### {matched['title']} ({matched['category']})\n\n"
                f"📍 **Venue**: {matched['venue']}\n"
                f"⏰ **Time**: {matched['start_time']} - {matched['end_time']}\n"
                f"👥 **Team Size**: {matched['min_team_size']}-{matched['max_team_size']} members\n"
                f"💰 **Registration Fee**: Rs. {matched['registration_fee']}\n\n"
                f"**Event Rules**:\n{rules_str}"
            )
        all_evs = get_all_events()
        events_str = "\n".join(f"• **{e['title']}** ({e['category']}) - {e['time']} at {e['venue']}" for e in all_evs[:4])
        return (
            f"Here are the highlighted events scheduled at FESTORA:\n\n{events_str}\n\n"
            f"For details or rule sheets for a specific event, ask for it by name!"
        )

    elif agent_type == "participant_agent":
        upper_q = question.upper()
        words = upper_q.replace(":", " ").replace(",", " ").replace(";", " ").split()
        for w in words:
            if "REG-" in w or w.isdigit():
                res = check_registration_status(w)
                if res.get("found"):
                    return (
                        f"Registration **{res.get('registration_id', w)}** status: **{res.get('payment_status')}** for *{res.get('event')}*.\n\n"
                        f"• **Team / Participant**: {res.get('team_name')}\n"
                        f"• **Team Leader**: {res.get('leader')}\n"
                        f"• **Members**: {res.get('members_count')}\n"
                        f"• **Fest Pass**: `{res.get('qr_pass')}`\n"
                        f"• **Gate Attendance**: {res.get('attendance')}"
                    )
            if "PASS" in w or "FEST-" in w:
                res = verify_qr_entry_pass(w)
                status_str = "GRANTED" if res.get("granted") else "DENIED"
                msg = res.get("message") or res.get("reason", "Pass processed.")
                return f"Gate Pass Check for `{w}`: **{status_str}**.\n\n{msg}"
        return (
            f"As a {role}, you can register individually or in teams for fest events. "
            f"After completing your registration and fee payment, a cryptographically signed Fest Pass with QR code "
            f"is automatically issued in your student dashboard for instant gate entry."
        )

    elif agent_type == "judging_agent":
        # Check if user is asking for rankings or scores of an event
        live_standings = get_live_event_results(question)
        if live_standings:
            event_name = live_standings[0].get("event", "Fest Event")
            lines = [f"🏆 **Live Standings for {event_name}**:\n"]
            for s_item in live_standings:
                lines.append(f"• **{s_item['position']}**: {s_item['team_name']} — Score: {s_item['total_score']}")
            return "\n".join(lines)

        rubric_data = get_evaluation_rubric("Technical")
        rubric_items = rubric_data.get("rubric", {})
        criteria_str = "\n".join(f"• **{name}**: {pts} pts" for name, pts in rubric_items.items())
        return (
            f"### Official Judging Rubric ({rubric_data.get('category', 'Technical')})\n\n"
            f"{criteria_str}\n\n"
            f"Scores are calculated out of {rubric_data.get('max_score', 100)} total points. "
            f"Evaluations are recorded live into the FESTORA database by authorized judges."
        )

    elif agent_type == "result_cert_agent":
        # Check if recipient or event mentioned
        live_standings = get_live_event_results(question)
        if live_standings:
            winner = live_standings[0]
            cert = generate_certificate_text(winner["team_name"], winner["event"], "1st Place Winner")
            return (
                f"🏆 **Official Winner Announcement & Certificate Verification**\n\n"
                f"**Event**: {winner['event']}\n"
                f"**Winner**: {winner['team_name']} ({winner['position']})\n"
                f"**Score**: {winner['total_score']}\n\n"
                f"📜 **Generated Certificate Text**:\n"
                f"> \"{cert['certificate_body']}\"\n\n"
                f"Verification ID: `{cert['certificate_id']}`"
            )
        return (
            f"🏆 **FESTORA Official Result & Certificate Announcement**\n\n"
            f"Certificates of Participation and Excellence are officially issued to all verified attendees and winners. "
            f"Each certificate includes an authentic tamper-proof Certificate Verification ID, verifiable publicly via the FESTORA portal."
        )

    elif agent_type == "sponsor_analytics_agent":
        analytics = get_fest_analytics()
        s = analytics["overview"]
        return (
            f"📊 **FESTORA Real-Time Analytics Report**\n\n"
            f"• **Registered Participants**: {s['total_registered_students']:,}\n"
            f"• **Total Active Events**: {s['total_events']}\n"
            f"• **Registration Revenue**: Rs. {s['total_revenue_inr']:,}\n"
            f"• **Sponsorship Capital**: Rs. {s['sponsor_funds_inr']:,}\n"
            f"• **QR Gate Check-in Rate**: {s['checkin_rate_percent']}%\n\n"
            f"Corporate sponsor deliverables and booth traffic tracking are operational."
        )

    else:
        return (
            f"Welcome to the FESTORA Helpdesk! 🎓\n\n"
            f"• **Registration Desk**: Student Activity Center, Desk #2\n"
            f"• **UPI Payments**: Verified automatically within 60 seconds; keep your Transaction ID handy.\n"
            f"• **Lost & Found / Medical**: Campus Health Center near Gate 1\n"
            f"• **Gate Entry**: Show your digital Fest Pass QR code at the entrance."
        )


# =====================================================================
# 1. SUPERVISOR AGENT
# =====================================================================

def supervisor_agent(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    user_role = state.get("user_role", "student")
    history = state.get("history", [])
    attempt = state.get("attempts", 0)

    prompt = f"""
You are the Supervisor Agent of the Modern College Fest Management System.

USER ROLE:
{user_role}

USER REQUEST:
{question}

Analyze the request and route to ONLY ONE of the following specialized agents:
- event_agent: Event details, schedules, timings, venues, rules, schedule clashes.
- participant_agent: Team registration, team size limits, member validation, QR entry pass, gate attendance.
- judging_agent: Scoring rubrics, judge evaluations, score calculations, team rankings.
- result_cert_agent: Publishing results, winner announcements, generating certificate text.
- sponsor_analytics_agent: Fest revenue, participant counts, footfall, sponsor packages and reports.
- faq_agent: General helpdesk, UPI payment issues, campus locations, directions.

Return ONLY the agent name (one of: event_agent, participant_agent, judging_agent, result_cert_agent, sponsor_analytics_agent, faq_agent).
Do not use markdown fences.
"""

    route = invoke_llm(prompt, "supervisor", state).strip().lower()

    valid_routes = {
        "event_agent",
        "participant_agent",
        "judging_agent",
        "result_cert_agent",
        "sponsor_analytics_agent",
        "faq_agent"
    }

    if route not in valid_routes:
        for r in valid_routes:
            if r in route:
                route = r
                break
        else:
            route = "faq_agent"

    new_history = list(history)
    new_history.append(f"Supervisor routed query to {route}")

    return {
        "route": route,
        "history": new_history,
        "attempts": attempt + 1
    }


# =====================================================================
# 2. EVENT MANAGEMENT AGENT
# =====================================================================

def event_management_agent(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])

    all_events = get_all_events()
    matched_event = get_event_details(question)

    prompt = f"""
You are the Event Management Agent of the College Fest Management System.

USER INQUIRY:
{question}

EVENT CATALOG DATA:
{all_events}

MATCHED EVENT DETAILS:
{matched_event}

Requirements:
1. Provide accurate event schedules, venues, and timings.
2. Clearly explain event rules and team size constraints.
3. If the user asks about schedule conflicts, specify whether timings or venues overlap.
4. Keep the answer structured, polite, and helpful for students and coordinators.

Return the final formatted answer.
Do not use markdown fences.
"""

    answer = invoke_llm(prompt, "event_agent", state)

    new_history = list(history)
    new_history.append("Event Management Agent resolved request")

    return {
        "agent_response": answer,
        "tool_outputs": {"matched_event": matched_event},
        "history": new_history,
        "attempts": attempt + 1
    }


# =====================================================================
# 3. PARTICIPANT & TEAM AGENT
# =====================================================================

def participant_team_agent(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])

    tools_context = {}
    if "REG-" in question.upper():
        words = question.upper().split()
        for w in words:
            if "REG-" in w:
                tools_context["registration_status"] = check_registration_status(w)
                break
    
    if "PASS-" in question.upper():
        words = question.upper().split()
        for w in words:
            if "PASS-" in w:
                tools_context["qr_pass_validation"] = verify_qr_entry_pass(w)
                break

    prompt = f"""
You are the Participant and Team Agent of the College Fest Management System.

USER INQUIRY:
{question}

SYSTEM REGISTRATION & ENTRY CONTEXT:
{tools_context}

Requirements:
1. Assist students with event registration, team formation, and member limits.
2. Explain QR entry pass requirements and gate check-in rules.
3. If payment or registration details are referenced, provide clear guidance.
4. Ensure instructions are welcoming and easy to follow.

Return the final formatted answer.
Do not use markdown fences.
"""

    answer = invoke_llm(prompt, "participant_agent", state)

    new_history = list(history)
    new_history.append("Participant & Team Agent processed request")

    return {
        "agent_response": answer,
        "tool_outputs": tools_context,
        "history": new_history,
        "attempts": attempt + 1
    }


# =====================================================================
# 4. JUDGING & EVALUATION AGENT
# =====================================================================

def judging_evaluation_agent(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])
    event_context = state.get("event_context", {})

    rubric = get_evaluation_rubric("Technical")
    scores_data = event_context.get("scores_list", [])
    rankings_data = []
    if scores_data:
        rankings_data = calculate_rankings(scores_data)

    prompt = f"""
You are the Judging & Evaluation Agent of the College Fest Management System.

USER INQUIRY:
{question}

OFFICIAL EVALUATION CRITERIA:
{rubric}

COMPUTED RANKINGS DATA (IF APPLICABLE):
{rankings_data}

Requirements:
1. Assist judges with marking criteria, rubric breakdown, and scoring weights.
2. If scores are provided, present a clear leaderboard with 1st, 2nd, and 3rd positions.
3. Provide constructive remarks and ensure evaluation fairness.
4. Maintain a formal, professional tone suitable for academic judging panels.

Return the final formatted answer.
Do not use markdown fences.
"""

    answer = invoke_llm(prompt, "judging_agent", state)

    new_history = list(history)
    new_history.append("Judging & Evaluation Agent processed request")

    return {
        "agent_response": answer,
        "tool_outputs": {"rankings": rankings_data, "rubric": rubric},
        "history": new_history,
        "attempts": attempt + 1
    }


# =====================================================================
# 5. RESULT & CERTIFICATE AGENT
# =====================================================================

def result_cert_agent(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])
    event_context = state.get("event_context", {})

    recipient = event_context.get("recipient", "Student Participant")
    event_name = event_context.get("event_name", "TechFest Event")
    position = event_context.get("position", "1st Place Winner")

    cert_data = generate_certificate_text(recipient, event_name, position)
    announcement_sample = draft_announcement(f"Winners Announced: {event_name}", f"Congratulations to {recipient}!")

    prompt = f"""
You are the Result and Certificate Agent of the College Fest Management System.

USER INQUIRY:
{question}

CERTIFICATE TEMPLATE CONTEXT:
{cert_data}

ANNOUNCEMENT FORMAT CONTEXT:
{announcement_sample}

Requirements:
1. Generate official, publication-ready result announcements or certificate text.
2. Include certificate verification ID, recipient name, event name, and position achieved.
3. Maintain an exciting, celebratory, and prestigious tone.

Return the final formatted text.
Do not use markdown fences.
"""

    answer = invoke_llm(prompt, "result_cert_agent", state)

    new_history = list(history)
    new_history.append("Result & Certificate Agent prepared publication")

    return {
        "agent_response": answer,
        "tool_outputs": {"certificate": cert_data},
        "history": new_history,
        "attempts": attempt + 1
    }


# =====================================================================
# 6. SPONSOR & ANALYTICS AGENT
# =====================================================================

def sponsor_analytics_agent(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])

    analytics = get_fest_analytics()
    sponsors = get_sponsor_reports()

    prompt = f"""
You are the Sponsor & Analytics Agent of the College Fest Management System.

USER INQUIRY:
{question}

CURRENT FEST ANALYTICS:
{analytics}

ACTIVE SPONSORSHIPS:
{sponsors}

Requirements:
1. Provide clear reporting on participant counts, revenue collected, and gate check-in rates.
2. Outline sponsorship tier benefits, deliverable commitments, and funding summaries.
3. Format figures clearly (e.g. INR currency, percentages).
4. Deliver insights tailored for College Fest Admins and Corporate Sponsors.

Return the final formatted report.
Do not use markdown fences.
"""

    answer = invoke_llm(prompt, "sponsor_analytics_agent", state)

    new_history = list(history)
    new_history.append("Sponsor & Analytics Agent generated report")

    return {
        "agent_response": answer,
        "tool_outputs": {"analytics": analytics, "sponsors": sponsors},
        "history": new_history,
        "attempts": attempt + 1
    }


# =====================================================================
# 7. GENERAL FAQ & HELPDESK AGENT
# =====================================================================

def faq_helpdesk_agent(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])

    prompt = f"""
You are the General FAQ & Helpdesk Agent for the College Fest.

USER INQUIRY:
{question}

Guidelines:
1. Assist users with general fest inquiries (UPI payment proof submission, campus entry points, lost & found, emergency contacts).
2. Advise that registration queries can be resolved at Student Activity Center Desk #2.
3. Be warm, welcoming, and concise.

Return the helpful response.
Do not use markdown fences.
"""

    answer = invoke_llm(prompt, "faq_agent", state)

    new_history = list(history)
    new_history.append("FAQ Helpdesk Agent assisted user")

    return {
        "agent_response": answer,
        "history": new_history,
        "attempts": attempt + 1
    }
