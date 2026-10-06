# Modern College Fest Management System - AI Agents Module

Welcome to the **AI Agents** component of the **Modern College Fest Management System**.
This module is built using **LangGraph** and powered by **Groq API** (Llama 3.3 70B) for lightning-fast, high-quality multi-agent responses.

---

## 📁 Project Structure

```text
fest_agents/
├── .env.example          # Template for GROQ_API_KEY configuration
├── state.py              # TypedDict defining AgentState shared across agents
├── tools/                # Specialized domain tools
│   ├── __init__.py       # Tool exports
│   ├── event_tools.py    # Event schedules, venues, rules & clash detection
│   ├── team_tools.py     # Team size check, registration status, QR entry passes
│   ├── judging_tools.py  # Evaluation rubrics, score calculations & team rankings
│   ├── analytics_tools.py# Fest statistics (revenue, footfall, check-ins, sponsors)
│   └── cert_tools.py     # Certificate text generator & announcement drafts
├── nodes.py              # Agent node implementations powered by ChatGroq
├── routers.py            # Routing logic based on supervisor intent classification
├── graph.py              # LangGraph StateGraph assembly and compiled application
├── run_demo.py           # Demonstration script with automated test cases & interactive mode
├── requirements.txt      # Dependencies (langgraph, langchain-groq, groq, python-dotenv)
└── README.md             # Documentation and usage guide
```

---

## 🔑 Groq API Setup

1. Get your free Groq API key from [Groq Console](https://console.groq.com/keys).
2. Create a `.env` file inside `fest_agents/` (or copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
3. Add your key inside `.env`:
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   ```

---

## 🤖 The AI Agents & Their Roles

| Agent Name | LLM Provider | Role in Fest Management |
| :--- | :--- | :--- |
| **Supervisor Agent** | Groq (Llama-3.3-70B) | Analyzes user queries & roles, dynamically routing requests to the appropriate specialist agent. |
| **Event Management Agent** | Groq (Llama-3.3-70B) | Handles event catalog, schedules, venue details, rule explanations, and timing conflict checks. |
| **Participant & Team Agent** | Groq (Llama-3.3-70B) | Validates team size criteria, verifies student registration status, and inspects QR entry passes. |
| **Judging & Evaluation Agent** | Groq (Llama-3.3-70B) | Assists judges with scoring rubrics, calculates weighted marks, and produces 1st/2nd/3rd leaderboards. |
| **Result & Certificate Agent** | Groq (Llama-3.3-70B) | Drafts official fest announcements, publishes results, and produces formal certificate text. |
| **Sponsor & Analytics Agent** | Groq (Llama-3.3-70B) | Generates real-time financial, attendance, footfall, and sponsorship reports for admins and partners. |
| **General FAQ & Helpdesk** | Groq (Llama-3.3-70B) | Answers general fest inquiries, UPI payment proof policies, lost-and-found, and campus directions. |

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Automated Test Suite
```bash
python run_demo.py
```

### 3. Run Interactive Chat Mode
```bash
python run_demo.py --interactive
```

---

## 🔌 Connecting to Django Backend

When integrating with Django REST Framework (DRF):

```python
# In your Django views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from fest_agents.graph import app

class FestAIChatView(APIView):
    def post(self, request):
        user_query = request.data.get("question", "")
        role = request.data.get("role", "student")
        
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
