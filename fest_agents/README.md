# Modern College Fest Management System - AI Agents Module

Welcome to the **AI Agents** component of the **Modern College Fest Management System**.
This module is built using **LangGraph** with a clean, modular multi-agent architecture designed specifically for college fest operations.

---

## 📁 Project Structure

```text
fest_agents/
├── state.py              # TypedDict defining AgentState shared across agents
├── tools/                # Specialized domain tools
│   ├── __init__.py       # Tool exports
│   ├── event_tools.py    # Event schedules, venues, rules & clash detection
│   ├── team_tools.py     # Team size check, registration status, QR entry passes
│   ├── judging_tools.py  # Evaluation rubrics, score calculations & team rankings
│   ├── analytics_tools.py# Fest statistics (revenue, footfall, check-ins, sponsors)
│   └── cert_tools.py     # Certificate text generator & announcement drafts
├── nodes.py              # Agent node implementations (Supervisor & Specialists)
├── routers.py            # Routing logic based on supervisor intent classification
├── graph.py              # LangGraph StateGraph assembly and compiled application
├── run_demo.py           # Demonstration script with automated test cases & interactive mode
├── requirements.txt      # Dependencies
└── README.md             # Documentation and usage guide
```

---

## 🤖 The AI Agents & Their Roles

| Agent Name | Role in Fest Management |
| :--- | :--- |
| **Supervisor Agent** | Analyzes user queries & roles, dynamically routing requests to the appropriate specialist agent. |
| **Event Management Agent** | Handles event catalog, schedules, venue details, rule explanations, and timing conflict checks. |
| **Participant & Team Agent** | Validates team size criteria, verifies student registration status, and inspects QR entry passes. |
| **Judging & Evaluation Agent** | Assists judges with scoring rubrics, calculates weighted marks, and produces 1st/2nd/3rd leaderboards. |
| **Result & Certificate Agent** | Drafts official fest announcements, publishes results, and produces formal certificate text. |
| **Sponsor & Analytics Agent** | Generates real-time financial, attendance, footfall, and sponsorship reports for admins and partners. |
| **General FAQ & Helpdesk** | Answers general fest inquiries, UPI payment proof policies, lost-and-found, and campus directions. |

---

## 🚀 How to Run

### 1. Install Dependencies (Optional)
```bash
pip install -r requirements.txt
```
*(Note: A built-in fallback simulation engine is included, so the demo will run and demonstrate multi-agent routing even before installing external packages or adding API keys!)*

### 2. Run Automated Test Suite
Test all 6 agent roles across sample student, coordinator, judge, and admin queries:
```bash
python run_demo.py
```

### 3. Run Interactive Chat Mode
Ask any query interactively:
```bash
python run_demo.py --interactive
```

---

## 🔌 Connecting to Django Backend (Future Step)

When your teammates finish the Django backend, you can connect this AI agent module with a single line of code in any Django View / DRF API View:

```python
# In your Django views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from fest_agents.graph import app

class FestAIChatView(APIView):
    def post(self, request):
        user_query = request.data.get("question", "")
        role = request.data.get("role", "student")
        
        # Invoke LangGraph AI system
        result = app.invoke({
            "question": user_query,
            "user_role": role,
            "history": [],
            "attempts": 0
        })
        
        return Response({
            "response": result.get("agent_response"),
            "route_taken": result.get("route"),
            "trace": result.get("history")
        })
```
