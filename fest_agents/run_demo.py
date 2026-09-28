"""
run_demo.py - Test and Demonstration Runner for College Fest AI Agents
Run this script to test all agents or interactively ask questions.
"""

import sys
import os

# Ensure the parent folder is in path so fest_agents can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fest_agents.graph import app
from fest_agents.state import AgentState


# Set utf-8 output encoding for Windows compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def print_separator(title=""):
    print("\n" + "=" * 70)
    if title:
        print(f" {title} ".center(70, "="))
        print("=" * 70)


def run_fest_query(question: str, role: str = "student", context: dict = None):
    """Executes a query through the LangGraph AI multi-agent system."""
    print_separator(f"TEST QUERY: [{role.upper()}]")
    print(f"User Input: \"{question}\"")
    
    initial_state: AgentState = {
        "question": question,
        "user_role": role,
        "event_context": context or {},
        "history": [],
        "attempts": 0
    }
    
    result = app.invoke(initial_state)
    
    print("\n--- EXECUTION TRACE ---")
    for step in result.get("history", []):
        print(f"  -> {step}")
    print(f"  -> Selected Route: {result.get('route')}")
    
    print("\n--- AGENT RESPONSE ---")
    print(result.get("agent_response", "No response generated."))
    return result


def run_all_test_cases():
    """Runs standard validation scenarios covering all fest system functions."""
    print_separator("COLLEGE FEST MANAGEMENT AI AGENTS - TEST SUITE")
    print("Running automated demonstration of all specialized agents...\n")
    
    # Test 1: Event Management Agent
    run_fest_query(
        question="What are the timings, venue, and team size rules for the Hackathon?",
        role="student"
    )
    
    # Test 2: Participant & Team Agent
    run_fest_query(
        question="I have a team with 3 members for Hackathon. Check registration status for REG-101 and QR pass PASS-CYBER-101.",
        role="student"
    )
    
    # Test 3: Judging & Evaluation Agent
    sample_scores = [
        {"team_name": "CyberKnights", "scores": {"innovation": 24, "tech": 25, "feasibility": 23, "presentation": 21}, "remarks": "Excellent live demo and clean API."},
        {"team_name": "MechaTitans", "scores": {"innovation": 20, "tech": 22, "feasibility": 24, "presentation": 21}, "remarks": "Good mechanical build, slight latency."},
        {"team_name": "CodeCrafters", "scores": {"innovation": 19, "tech": 20, "feasibility": 22, "presentation": 20}, "remarks": "Creative concept, needs more testing."}
    ]
    run_fest_query(
        question="Evaluate and rank the Hackathon final round teams based on judge scores.",
        role="judge",
        context={"scores_list": sample_scores}
    )
    
    # Test 4: Result & Certificate Agent
    run_fest_query(
        question="Generate official certificate text and draft announcement for Aarav Sharma winning 1st place in TechSprint Hackathon.",
        role="coordinator",
        context={
            "recipient": "Aarav Sharma",
            "event_name": "TechSprint 24-Hour Hackathon",
            "position": "1st Place Winner"
        }
    )
    
    # Test 5: Sponsor & Analytics Agent
    run_fest_query(
        question="Give me the total fest revenue, student registration numbers, footfall, and sponsor funding report.",
        role="admin"
    )
    
    # Test 6: General FAQ Agent
    run_fest_query(
        question="How do I submit UPI payment proof if the transaction is pending, and where is the helpdesk?",
        role="student"
    )
    
    print_separator("ALL AGENT TESTS COMPLETED SUCCESSFULLY")


def interactive_mode():
    """Interactive loop for user to test custom queries."""
    print_separator("INTERACTIVE FEST AI ASSISTANT")
    print("Type your questions as a student, judge, coordinator, or admin.")
    print("Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            user_input = input("\nEnter your fest query: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting interactive mode. Have a great fest!")
                break
            
            role = input("Enter your role (student/coordinator/judge/sponsor/admin) [default: student]: ").strip() or "student"
            run_fest_query(question=user_input, role=role)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        run_all_test_cases()
        print("\nTip: Run 'python run_demo.py --interactive' to chat interactively with the agents!")
