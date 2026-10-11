"""
routers.py - Routing logic for College Fest AI Agents
"""

from .state import AgentState

VALID_ROUTES = {
    "event_agent",
    "participant_agent",
    "judging_agent",
    "result_cert_agent",
    "sponsor_analytics_agent",
    "faq_agent"
}


def route_supervisor(state: AgentState) -> str:
    """
    Evaluates the route chosen by the supervisor agent and returns the destination node name.
    If the route is unrecognized or missing, defaults to faq_agent.
    """
    destination = state.get("route", "").strip().lower()
    
    if destination in VALID_ROUTES:
        return destination
    
    # Fallback to general FAQ agent
    return "faq_agent"
