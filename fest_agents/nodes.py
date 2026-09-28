"""
nodes.py - Agent nodes for College Fest Management System using Groq API
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq

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
    get_fest_analytics,
    get_sponsor_reports,
    generate_certificate_text,
    draft_announcement
)

# Load environment variables from .env file
load_dotenv()

# Initialize Groq LLM using Groq API Key
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    api_key=groq_api_key
)


# =====================================================================
# 1. SUPERVISOR AGENT (Intent Classifier & Router)
# =====================================================================

def supervisor_agent(state: AgentState) -> Dict[str, Any]:
    """
    Supervisor Agent that analyzes the user's inquiry and role,
    then directs the workflow to the specialized fest agent via Groq LLM.
    """
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

    response = llm.invoke(prompt)
    route = response.content.strip().lower()

    # Clean markdown fences if any
    if route.startswith("```"):
        route = route.replace("```", "").strip()

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
    """
    Handles event schedules, rules, venue details, and conflict checks.
    """
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])

    # Fetch tool context
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

    response = llm.invoke(prompt)
    answer = response.content.strip()

    if answer.startswith("```"):
        answer = answer.strip("`").strip()

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
    """
    Handles team registration, team size validation, entry passes, and attendance.
    """
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])

    # Tool checks: registration lookup or QR pass validation
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

    response = llm.invoke(prompt)
    answer = response.content.strip()

    if answer.startswith("```"):
        answer = answer.strip("`").strip()

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
    """
    Assists judges with evaluation rubrics, scores calculation, and ranking generation.
    """
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])
    event_context = state.get("event_context", {})

    # Tool execution: Rubric lookup or ranking calculation
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

    response = llm.invoke(prompt)
    answer = response.content.strip()

    if answer.startswith("```"):
        answer = answer.strip("`").strip()

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
    """
    Generates official winner announcements, certificate text, and result publications.
    """
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

    response = llm.invoke(prompt)
    answer = response.content.strip()

    if answer.startswith("```"):
        answer = answer.strip("`").strip()

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
    """
    Provides dashboards, revenue reports, footfall stats, and sponsor management data.
    """
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

    response = llm.invoke(prompt)
    answer = response.content.strip()

    if answer.startswith("```"):
        answer = answer.strip("`").strip()

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
    """
    Provides general assistance: UPI payment FAQs, campus directions, and emergency desk.
    """
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

    response = llm.invoke(prompt)
    answer = response.content.strip()

    if answer.startswith("```"):
        answer = answer.strip("`").strip()

    new_history = list(history)
    new_history.append("FAQ Helpdesk Agent assisted user")

    return {
        "agent_response": answer,
        "history": new_history,
        "attempts": attempt + 1
    }
