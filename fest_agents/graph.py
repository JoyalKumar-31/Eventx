"""
graph.py - LangGraph Multi-Agent Workflow for College Fest Management
"""

from typing import Dict, Any

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

try:
    from langgraph.graph import StateGraph, END
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False


def build_fest_graph():
    """
    Constructs and compiles the StateGraph workflow for the college fest agents.
    """
    if not HAS_LANGGRAPH:
        # Fallback runner in case user runs demo before installing langgraph package
        class StandaloneFestRunner:
            def invoke(self, state: AgentState) -> Dict[str, Any]:
                current_state = dict(state)
                # 1. Run supervisor
                sup_result = supervisor_agent(current_state)
                current_state.update(sup_result)
                
                # 2. Route to specialized agent
                destination = route_supervisor(current_state)
                agent_map = {
                    "event_agent": event_management_agent,
                    "participant_agent": participant_team_agent,
                    "judging_agent": judging_evaluation_agent,
                    "result_cert_agent": result_cert_agent,
                    "sponsor_analytics_agent": sponsor_analytics_agent,
                    "faq_agent": faq_helpdesk_agent,
                }
                worker_func = agent_map.get(destination, faq_helpdesk_agent)
                agent_result = worker_func(current_state)
                current_state.update(agent_result)
                return current_state
                
        return StandaloneFestRunner()

    # Standard LangGraph StateGraph assembly
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


# Pre-compiled application graph instance ready for import
app = build_fest_graph()
