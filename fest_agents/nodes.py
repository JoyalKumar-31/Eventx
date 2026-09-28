"""
nodes.py - Agent nodes for College Fest Management System
Each agent follows the prompt-execution-cleanup-state pattern.
"""

import os
from typing import Dict, Any

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


# =====================================================================
# LLM Loader with Smart Fallback (Runs even without external API keys!)
# =====================================================================

class FallbackFestLLM:
    """
    Simulated LLM engine that produces realistic responses when no external
    LLM API key (OpenAI/Google) is configured. Ensures the project runs out-of-the-box!
    """
    class Response:
        def __init__(self, content: str):
            self.content = content

    def invoke(self, prompt: str):
        prompt_lower = prompt.lower()
        
        # Supervisor routing decisions
        if "route to only one" in prompt_lower or "supervisor agent" in prompt_lower:
            # Look specifically inside USER REQUEST section
            user_text = prompt_lower
            if "user request:" in prompt_lower:
                user_text = prompt_lower.split("user request:")[1]
                if "analyze the request" in user_text:
                    user_text = user_text.split("analyze the request")[0]

            # Prioritize specific intents first
            if any(k in user_text for k in ["certificate", "announcement", "result", "winner"]):
                return self.Response("result_cert_agent")
            elif any(k in user_text for k in ["sponsor", "analytics", "revenue", "footfall", "funding"]):
                return self.Response("sponsor_analytics_agent")
            elif any(k in user_text for k in ["judge", "score", "rubric", "evaluation", "rank"]):
                return self.Response("judging_agent")
            elif any(k in user_text for k in ["qr pass", "pass-", "reg-", "attendance", "check-in"]):
                return self.Response("participant_agent")
            elif any(k in user_text for k in ["event", "schedule", "clash", "venue", "timing", "timing", "hackathon", "robowars"]):
                return self.Response("event_agent")
            elif any(k in user_text for k in ["team", "register", "participant", "member"]):
                return self.Response("participant_agent")
            return self.Response("faq_agent")
        
        # Event Management fallback
        if "event management agent" in prompt_lower:
            return self.Response(
                "Here are the event details:\n"
                "- Event: TechSprint 24-Hour Hackathon\n"
                "- Venue: Main Computer Lab (Block A)\n"
                "- Schedule: Day 1, 10:00 AM to Day 2, 10:00 AM\n"
                "- Team Size: 2 to 4 members | Fee: Rs. 500\n"
                "- Core Rules: Code must be built within 24 hours. Pre-existing templates are disallowed. GitHub commits mandatory.\n"
                "No schedule conflicts detected."
            )
            
        # Participant & Team fallback
        if "participant and team agent" in prompt_lower:
            return self.Response(
                "Participant & Team Validation Status:\n"
                "✓ Eligibility: The proposed team structure meets the fest regulations (2-4 members for Hackathon).\n"
                "✓ Entry Pass: Digital QR passes will be unlocked upon payment confirmation.\n"
                "Note: Please keep your college student ID card handy at the registration desk for verification."
            )
            
        # Judging & Evaluation fallback
        if "judging & evaluation agent" in prompt_lower:
            return self.Response(
                "[OFFICIAL EVALUATION & RANKINGS]\n"
                "1. Rank #1 (Winner): Team CyberKnights - Score: 93/100 (Exceptional innovation & clean architecture)\n"
                "2. Rank #2 (Runner Up): Team MechaTitans - Score: 87/100 (Strong technical execution and robust design)\n"
                "3. Rank #3 (2nd Runner Up): Team CodeCrafters - Score: 81/100 (Creative concept, needs UI polish)\n"
                "Evaluation adheres to official 100-point rubric."
            )
            
        # Result & Certificate fallback
        if "result and certificate agent" in prompt_lower:
            return self.Response(
                "[CERTIFICATE & RESULT DISPATCH]\n"
                "- Document: Official Certificate of Excellence\n"
                "- Recipient: Aarav Sharma (Team CyberKnights)\n"
                "- Event: TechSprint 24-Hour Hackathon (1st Place Winner)\n"
                "- Verification ID: CERT-FEST-84921\n"
                "- Public Announcement: Drafted and queued for the student portal banner."
            )
            
        # Sponsor & Analytics fallback
        if "sponsor & analytics agent" in prompt_lower:
            return self.Response(
                "[FEST ANALYTICS & SPONSORSHIP SUMMARY]\n"
                "- Total Registered Students: 1,420 across 18 events\n"
                "- Registration Revenue: Rs. 2,85,000\n"
                "- Confirmed Sponsorships: Rs. 4,50,000 (Title: TechNova, Associate: CloudSprint)\n"
                "- Gate Footfall Check-in Rate: 83.1% via QR scanner verification."
            )
            
        # Default FAQ response
        return self.Response(
            "Welcome to the College Fest Helpdesk! For UPI payment receipt verifications, "
            "visit Counter #2 at the Student Activity Center. Event gates open at 8:30 AM daily."
        )


def _get_llm():
    """Initializes external LLM if API keys are set, otherwise uses FallbackFestLLM."""
    if os.environ.get("OPENAI_API_KEY"):
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        except Exception:
            pass
    if os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
        except Exception:
            pass
    return FallbackFestLLM()


llm = _get_llm()


# =====================================================================
# 1. SUPERVISOR AGENT (Intent Classifier & Router)
# =====================================================================

def supervisor_agent(state: AgentState) -> Dict[str, Any]:
    """
    Supervisor Agent that analyzes the user's inquiry and role,
    then directs the workflow to the specialized fest agent.
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

Return ONLY the agent name (e.g. event_agent, participant_agent, judging_agent, result_cert_agent, sponsor_analytics_agent, or faq_agent).
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

    # Example tool check: team size validation or registration lookup
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
