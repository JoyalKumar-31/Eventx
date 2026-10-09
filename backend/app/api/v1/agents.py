import sys
import os
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.dependencies import get_current_user_optional, get_db
from app.models.user import User

# Ensure workspace root is in sys.path to load fest_agents module
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

try:
    from fest_agents.graph import app as agents_app
    from fest_agents.nodes import get_llm
except ImportError as e:
    raise ImportError(f"Failed to import fest_agents: {e}")

router = APIRouter(prefix="/agents", tags=["Fest AI Agents"])


class AgentChatRequest(BaseModel):
    question: str = Field(..., description="The user query or instruction for the AI agents")
    role: Optional[str] = Field(None, description="Role context: student, event_coordinator, judge, admin")
    event_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional contextual data (active event, team, etc.)")
    history: Optional[List[str]] = Field(default_factory=list, description="Recent conversation turns")


class AgentChatResponse(BaseModel):
    success: bool
    response: str
    route_taken: Optional[str] = None
    trace: List[str] = []
    user_role: str
    agent_name: str


ROLE_AGENT_NAMES = {
    "supervisor": "Fest Supervisor Agent",
    "event_agent": "Event Management & Schedule Agent",
    "participant_agent": "Participant & Team Agent",
    "judging_agent": "Judging & Evaluation Agent",
    "result_cert_agent": "Result & Certificate Agent",
    "sponsor_analytics_agent": "Sponsor & Analytics Agent",
    "faq_agent": "Campus Helpdesk & FAQ Agent",
}


@router.post("/chat", response_model=AgentChatResponse)
def chat_with_agents(
    req: AgentChatRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Direct interface to the LangGraph multi-agent fest copilot.
    Routes queries dynamically across 7 specialized agents.
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Determine role: Prefer authenticated user role if present, else fallback to request role, else "student"
    user_role = "student"
    if current_user:
        user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role).lower()
    elif req.role:
        user_role = req.role.lower().strip()

    context = req.event_context or {}
    if current_user:
        context["user_id"] = current_user.id
        context["user_email"] = current_user.email
        context["user_name"] = current_user.full_name

    initial_state = {
        "question": req.question.strip(),
        "user_role": user_role,
        "event_context": context,
        "history": req.history or [],
        "attempts": 0
    }

    try:
        result = agents_app.invoke(initial_state)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI Agent execution failed: {str(exc)}"
        )

    route_taken = result.get("route", "faq_agent")
    agent_display = ROLE_AGENT_NAMES.get(route_taken, "Fest AI Assistant")

    return AgentChatResponse(
        success=True,
        response=result.get("agent_response", "I'm sorry, I couldn't process your inquiry at this moment."),
        route_taken=route_taken,
        trace=result.get("history", []),
        user_role=user_role,
        agent_name=agent_display
    )


@router.get("/suggestions")
def get_prompt_suggestions(
    role: Optional[str] = "student",
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Returns quick interactive prompt chips tailored to user role.
    """
    effective_role = role or "student"
    if current_user:
        effective_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role).lower()

    effective_role = effective_role.lower()

    suggestions_by_role = {
        "student": [
            "What events are scheduled for today?",
            "Check my registration status and QR pass",
            "What are the rules and team size for Coding?",
            "How do I submit UPI payment proof if pending?",
            "Is there any clash between Coding and BGMI?",
        ],
        "event_coordinator": [
            "Show participant rosters and registered squads",
            "What are the evaluation criteria rubrics for my event?",
            "Draft official winner announcement",
            "Check if any other events clash with my schedule",
            "How do I verify attendee check-ins?",
        ],
        "judge": [
            "Show official evaluation scoring rubric and weightages",
            "How are team scores and rankings calculated?",
            "What events are assigned to me for evaluation?",
            "What is the maximum score per criteria?",
        ],
        "admin": [
            "Show total fest footfall, revenue, and check-in rate",
            "Show active sponsorship tiers and funding report",
            "Give me a summary of registered students and events",
            "Which events have the highest participant turnout?",
        ]
    }

    return {
        "role": effective_role,
        "suggestions": suggestions_by_role.get(effective_role, suggestions_by_role["student"])
    }


@router.get("/status")
def get_agents_status() -> Dict[str, Any]:
    """
    Returns health status of the multi-agent system and LLM backend.
    """
    llm = get_llm()
    return {
        "status": "online",
        "llm_engine": "Groq Llama 3.3 70B (Versatile)" if llm else "Rule-Engine & Database Fallback Intelligence",
        "llm_connected": bool(llm),
        "agents": list(ROLE_AGENT_NAMES.values())
    }
