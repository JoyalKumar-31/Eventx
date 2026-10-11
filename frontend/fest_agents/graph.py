"""
graph.py - LangGraph Multi-Agent Workflow for College Fest Management
"""

from langgraph.graph import StateGraph, END
from .state import AgentState
from .routers import route_supervisor
from .nodes import (
    supervisor_agent,
    event_management_agent,
    participant_team_agent,
    judging_evaluation_agent,
    result_cert_agent,
    sponsor_analytics_agent,
    faq_helpdesk_agent
)


def build_fest_graph():
    """
    Constructs and compiles the StateGraph workflow for the college fest agents.
    """
    workflow = StateGraph(AgentState)

    # 1. Register all agent nodes
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("event_agent", event_management_agent)
    workflow.add_node("participant_agent", participant_team_agent)
    workflow.add_node("judging_agent", judging_evaluation_agent)
    workflow.add_node("result_cert_agent", result_cert_agent)
    workflow.add_node("sponsor_analytics_agent", sponsor_analytics_agent)
    workflow.add_node("faq_agent", faq_helpdesk_agent)

    # 2. Set entry point
    workflow.set_entry_point("supervisor")

    # 3. Add conditional routing from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "event_agent": "event_agent",
            "participant_agent": "participant_agent",
            "judging_agent": "judging_agent",
            "result_cert_agent": "result_cert_agent",
            "sponsor_analytics_agent": "sponsor_analytics_agent",
            "faq_agent": "faq_agent"
        }
    )

    # 4. Connect each specialist agent to END
    workflow.add_edge("event_agent", END)
    workflow.add_edge("participant_agent", END)
    workflow.add_edge("judging_agent", END)
    workflow.add_edge("result_cert_agent", END)
    workflow.add_edge("sponsor_analytics_agent", END)
    workflow.add_edge("faq_agent", END)

    # 5. Compile the graph
    app = workflow.compile()
    return app


# Pre-compiled application graph instance ready for execution
app = build_fest_graph()
