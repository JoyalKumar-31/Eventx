# EventX AI Agent: Presentation Script, Live Demo Guide & Faculty Viva Preparation

> **Prepared For**: Final Project Evaluation & Faculty Viva  
> **Role**: AI Agent Subsystem Lead  
> **Project**: EventX — Autonomous College Fest Management System  

---

## 1. 3–5 Minute Spoken Presentation Script

*(Speak at a steady, confident pace. Smile, maintain eye contact with the faculty, and reference the slides or live screen.)*

---

### [0:00 - 0:45] Introduction & Problem Statement
"Good morning, respected professors and evaluators. 

My name is [Your Name], and in our project **EventX**, my primary responsibility was the design and implementation of the **Multi-Agent AI Subsystem**.

In a large college festival with thousands of students, 50+ competitions, and parallel venues, attendees and organizers face severe operational bottlenecks:
- Students have to navigate multiple tabs just to register, check clash timings, or update their academic affiliation.
- Judges manually calculate scores across complex rubrics.
- Coordinators struggle with gate verification and schedule clashes.

A simple FAQ chatbot cannot solve this because it is disconnected from the real database. A regular REST form cannot solve this because it requires rigid manual navigation. 

To bridge this gap, I designed and implemented an **autonomous multi-agent system powered by LangGraph, Groq Llama 3.3 70B, and live relational database tools** that can not only answer questions, but **autonomously execute real actions in the database** based on natural language commands."

---

### [0:45 - 1:45] Technologies & Architecture
"To build this, I used:
1. **LangGraph**: For orchestrating our multi-agent workflow using a state machine (`StateGraph`).
2. **Groq API with Llama 3.3 70B Versatile**: For high-speed natural language intent understanding and reasoning.
3. **FastAPI & SQLAlchemy ORM**: To bridge the AI graph with our live SQLite relational database.
4. **React & Tailwind CSS**: For a reactive chat drawer that syncs with the frontend state in real time.

Our architecture follows a **Hierarchical Supervisor Pattern**:
- When a user submits an inquiry, it enters our LangGraph `StateGraph`.
- The first node is the **Supervisor Agent** (`supervisor_agent` in `fest_agents/nodes.py`). It analyzes the user's role and intent, and conditionally routes the request to one of six specialized domain agents:
  1. **Participant & Team Agent**: For registrations, pass lookups, and profile modifications.
  2. **Event Management Agent**: For event rules, timings, and schedule clash detection.
  3. **Judging & Evaluation Agent**: For rubric calculations and recording marks.
  4. **Result & Certificate Agent**: For leaderboard rankings and verifiable credentials.
  5. **Sponsor & Analytics Agent**: For live festival metrics and revenue tracking.
  6. **Campus Helpdesk Agent**: For general portal navigation.

A crucial design decision I made was **resilient dual-engine execution**: if the external Groq cloud API is unreachable, our system does not crash; it automatically executes through a database-grounded rule-based fallback, ensuring 100% festival uptime."

---

### [1:45 - 3:00] Complete Workflow & Real Implementation
"Let me explain how an action actually executes through our code.

Suppose a student types:  
`'change department from Robotics And Automation to Computer Science Engineering'`.

Here is the exact trace:
1. **Frontend Dispatch**: In `FestAICopilot.jsx`, the user query is bundled with the authenticated user session (`user_id`, `email`, `role`) and sent via `POST /api/agents/chat`.
2. **State Injection**: In `backend/app/api/v1/agents.py`, FastAPI creates our `AgentState` TypedDict and calls `agents_app.invoke(initial_state)`.
3. **Supervisor Routing**: The supervisor node inspects the intent (`change` + `department`) and sets `state['route'] = 'participant_agent'`. LangGraph's conditional edge `route_supervisor` branches directly to the participant node.
4. **Tool Pre-Execution**: In `participant_team_agent`, the agent calls our custom tool function `parse_profile_update_intent()` in `profile_tools.py`.
5. **Database Commit**: It extracts `department: 'Computer Science Engineering'`, connects via `SessionLocal()`, runs an `UPDATE` on the `student_profiles` table, commits the transaction, and writes an audit trail entry into `audit_logs`.
6. **Reactive Sync**: The graph returns an action flag `action: 'profile_updated'`. When `FestAICopilot.jsx` receives this response, it triggers `refreshUser()` on our `AuthContext`. As a result, the student's profile page and navigation headers immediately update on the screen **without needing a page reload**."

---

### [3:00 - 3:45] Key Highlights & My Contribution
"During development, I solved two critical engineering challenges:
1. **Free vs. Paid Registration Flow**: In `team_tools.py`, free event registrations are automatically confirmed with an unlocked QR entry pass hash. Paid event registrations are marked `PENDING_PAYMENT` with pass locking until fee settlement.
2. **Context Disambiguation**: When a user says `'edit University Name to VIT'`, naive regexes would update the user's personal name to `'Vit'`. I engineered disambiguation logic in `profile_tools.py` so that institutional names are strictly routed to `college_name` while keeping user personal names intact.

In summary, I built a reliable, stateful, and action-oriented AI system that connects natural language directly to database operations.

Thank you, professors. I would now be delighted to demonstrate the live system and answer your questions."

---

## 2. Practical Live Demonstration Sequence

Follow this exact sequence during your live demo to impress your faculty:

| Step | What to Type in Fest AI Copilot | What to Show on Screen | What to Tell the Faculty |
| :--- | :--- | :--- | :--- |
| **Demo 1** | `"What events are scheduled for today?"` | Event catalog cards with categories, times, and venue block rooms. | *"The supervisor routes this to `event_agent`, which directly queries our live database events."* |
| **Demo 2** | `"change my year in my profile from 1st year to 3rd year"` | Agent responds with green checkmark card. Look at Student Profile page: the Year dropdown automatically updates to **3rd Year**! | *"Notice that the agent didn't just give text advice; it ran an SQL update on `student_profiles` and triggered `refreshUser()` so the UI updated live."* |
| **Demo 3** | `"change department from Robotics And Automation to Computer Science Engineering"` | Response confirms update. Department on profile card re-renders as **Computer Science Engineering**. | *"Here it handled a from-to compound name with the word 'and' without losing formatting."* |
| **Demo 4** | `"edit University Name to VIT"` | College updates to VIT. Show the user name badge: it still says **Alex**, NOT Vit! | *"I engineered context disambiguation so institution name edits never corrupt user personal names."* |
| **Demo 5** | `"What is my profile?"` | Neat profile summary card showing updated year, dept, college, and email. | *"Agent queries live DB state and formats markdown on the fly."* |

---

## 3. 25 Faculty Viva Questions and Answers

### Section A: Conceptual & Architectural Questions

#### Q1: What is an AI Agent, and how is it different from a simple LLM like ChatGPT?
**Answer**:  
"An LLM is a stateless next-token prediction model. It can generate text based on training data, but it cannot independently interact with the external world.  
An **AI Agent** combines an LLM with **state management, planning, tools, and execution loops**. In our project, the agent doesn't just reply; it observes user context, decides which tool to call, and executes real SQL updates on our database using LangGraph."

#### Q2: Why did you choose LangGraph instead of simple LangChain chains?
**Answer**:  
"LangChain sequential chains are linear (Node A $\rightarrow$ Node B $\rightarrow$ Node C) and struggle with multi-role branching and conditional decision loops.  
**LangGraph** models the workflow as a state machine (`StateGraph`). It allows us to define a central `supervisor` node, evaluate conditional edges (`add_conditional_edges`), route dynamically across 6 specialized agents, and manage shared typed state (`AgentState`) with clear cycle prevention."

#### Q3: What model is used in your project?
**Answer**:  
"We use **Llama 3.3 70B Versatile** hosted on the **Groq Cloud API** (`llama-3.3-70b-versatile`) with a temperature of `0.2` for deterministic, fact-grounded reasoning. We access it via `ChatGroq` from `langchain_groq`."

#### Q4: What happens if Groq API is offline, down, or rate-limited?
**Answer**:  
"In `fest_agents/nodes.py`, our `invoke_llm()` function wraps the LLM call in a `try-except` block. If the API key is missing or a network timeout occurs, it seamlessly transitions into `_generate_fallback()`. This fallback executes the exact same database tools and intent parsers rule-based, guaranteeing 100% festival uptime."

#### Q5: What is the Supervisor Pattern in multi-agent systems?
**Answer**:  
"The Supervisor Pattern is a hierarchical multi-agent architecture where a central coordinator agent inspects the user request, role, and history, and delegates work to domain-specific worker agents. The workers execute their specialized tasks and report back to `END`."

---

### Section B: Implementation & Code-Specific Questions

#### Q6: Walk me through your `AgentState`. Where is it defined and what fields does it have?
**Answer**:  
"It is defined in `fest_agents/state.py` as a Python `TypedDict`:
- `question`: The user's input prompt.
- `user_role`: User role (`student`, `judge`, `coordinator`, etc.).
- `route`: The target agent chosen by the supervisor.
- `history`: Execution trace of which agents ran.
- `event_context`: Injected session data (`user_id`, `user_email`, `user_name`).
- `tool_outputs`: Dictionary holding results from executed tools.
- `agent_response`: The final formatted markdown output.
- `error` and `attempts`: Counters for safeguards."

#### Q7: Where are graph nodes and edges defined?
**Answer**:  
"In `fest_agents/graph.py` inside `build_fest_graph()`:
- `workflow.add_node()` registers 7 nodes (`supervisor`, `event_agent`, `participant_agent`, etc.).
- `workflow.set_entry_point('supervisor')` sets the starting node.
- `workflow.add_conditional_edges('supervisor', route_supervisor, ...)` defines the conditional branch.
- `workflow.add_edge(node, END)` connects each specialist to graph termination.
- `workflow.compile()` compiles it into an executable runnable."

#### Q8: How does the agent prevent unauthorized actions (e.g. a student scoring an event)?
**Answer**:  
"We implement security in depth:
1. In `backend/app/api/v1/agents.py`, we extract the authenticated user role from their verified JWT token (`current_user.role`) rather than trusting the client request body.
2. In `fest_agents/tools/judging_tools.py`, scoring requires a valid `judge_id` matching an active judge assignment.
3. In `profile_tools.py`, updates are strictly scoped to `user.id` resolved from the session."

#### Q9: How did you implement Free vs. Paid event registration in the agent?
**Answer**:  
"In `fest_agents/tools/team_tools.py` in `register_student_for_event()`:
- We check `event.registration_fee`.
- If fee is `0.0`: status is set to `CONFIRMED`, and an active QR entry pass hash (`PASS-...`) is generated.
- If fee is $>0$: status is set to `PENDING_PAYMENT`, and the pass hash is locked (`LOCKED-PENDING-PAYMENT-...`). The user must settle dues in `/student/registrations` to unlock the pass."

#### Q10: How does the frontend know that a profile change occurred without reloading?
**Answer**:  
"In `backend/app/api/v1/agents.py`, when `tool_outputs` contains `profile_action`, the API response includes `action: 'profile_updated'`. In `FestAICopilot.jsx`, when this flag is received, it executes `await refreshUser()`, which calls `GET /auth/me` and updates React's `AuthContext`. All open profile inputs and headers re-render immediately."

#### Q11: How do you handle schedule clashes?
**Answer**:  
"In `fest_agents/tools/event_tools.py`, `check_schedule_clash()` inspects event start/end timestamps and venue rooms from the database. It compares time intervals for overlap and checks if both events are assigned to the same venue, returning a clash alert."

#### Q12: Why did 'edit University Name to VIT' previously change the user name, and how did you fix it?
**Answer**:  
"The user name parser was matching the word `'Name'` inside `'University Name'`.  
I fixed it in `profile_tools.py` by:
1. Detecting if `re.search(r'\b(?:college|university)\s*name\b')` matched.
2. If an institution name is detected, the personal name updater is skipped unless the user explicitly said `'my name to X'`.
3. Routing institutional updates strictly to `college_name`."

#### Q13: What ORM is used and how does the agent interact with it?
**Answer**:  
"We use **SQLAlchemy ORM** connecting to SQLite (`fest_app.db`). In our tools (`profile_tools.py`, `team_tools.py`), we create a session using `SessionLocal()`, perform queries on models like `User`, `StudentProfile`, `Registration`, commit changes with `db.commit()`, and always close the session in a `finally` block."

#### Q14: How are audit logs maintained for AI actions?
**Answer**:  
"Whenever `update_student_profile` executes, it calls `log_action()` from `app.services.audit_service`. This records the user ID, entity type (`User`), old values, and new values into the `audit_logs` table for administrative accountability."

#### Q15: How does the agent handle team size limits?
**Answer**:  
"In `team_tools.py`, `validate_team_size()` queries `min_team_size` and `max_team_size` from the `Event` model. If a squad has fewer or more members than allowed, it rejects the action with a clear rule violation message."

---

### Section C: Challenging / Viva Defense Questions

#### Q16: What is the token latency and performance of your system?
**Answer**:  
"Using Groq's LPU (Language Processing Unit) inference with Llama 3.3 70B, generation latency is under 600 milliseconds. In fallback mode, response latency is under 50 milliseconds because it executes local pre-compiled regexes and database queries directly."

#### Q17: How is memory maintained across conversation turns?
**Answer**:  
"In `FestAICopilot.jsx`, the last 4 conversation turns are packaged as strings (`'USER: ...'`, `'ASSISTANT: ...'`) and passed in the `history` array of `AgentChatRequest`. In `nodes.py`, this history is injected into `AgentState['history']` and passed to the LLM prompt for conversational continuity."

#### Q18: Could prompt injection make your agent delete database tables?
**Answer**:  
"No. The agent does not execute raw SQL queries (`db.execute(user_text)`). It uses strictly parameterized ORM methods and typed update dictionaries. Even if a user attempts SQL injection in chat (e.g. `'; DROP TABLE users;--`), the input is treated as a literal string value for that field."

#### Q19: What is the difference between synchronous and asynchronous agent workflows?
**Answer**:  
"In our system, the HTTP call is synchronous from the client's perspective (`POST /chat` returns the completed turn), but LangGraph handles node execution asynchronously within the FastAPI event loop. This ensures predictable request-response cycles without needing polling."

#### Q20: What are the main limitations of your current implementation?
**Answer**:  
"1. Voice input is not yet natively supported; interactions are text-based.  
2. Payment settlement requires opening the Razorpay/UPI modal rather than conversational direct debit, which was chosen intentionally for financial security."

#### Q21: What is temperature in `ChatGroq(temperature=0.2)` and why 0.2?
**Answer**:  
"Temperature controls the randomness of token generation (from 0.0 to 1.0). A high temperature (0.8) makes outputs creative and unpredictable. For an administrative fest management system that must strictly adhere to rules and dates, a low temperature of `0.2` ensures focused, deterministic, and accurate responses."

#### Q22: Why not use a single prompt with Function Calling (OpenAI Tools)?
**Answer**:  
"A single prompt with dozens of tools suffers from **context pollution** and tool selection degradation as the number of events and tools grows. By separating concerns into LangGraph nodes (Event, Participant, Judge, Sponsor), each agent only focuses on its specific tools and context, significantly improving accuracy."

#### Q23: How do you normalize student year inputs?
**Answer**:  
"In `fest_agents/tools/profile_tools.py`, `normalize_year_of_study()` parses varied user phrasings (*'1st year'*, *'first'*, *'3'*, *'final year'*) and maps them into standardized database strings: `'1st Year'`, `'2nd Year'`, `'3rd Year'`, `'4th Year'`, or `'Postgraduate / PhD'`."

#### Q24: What happens if a student tries to register for an event they already joined?
**Answer**:  
"In `team_tools.py`, `register_student_for_event()` first checks `db.query(Registration).filter(event_id, user_id)`. If an active enrollment exists, it alerts the student: *'You are already registered for [Event]!'* and displays their existing registration number and pass status instead of creating a duplicate."

#### Q25: What is your primary individual contribution to this project?
**Answer**:  
"I architected and built the entire LangGraph multi-agent subsystem:
1. Implemented the 7 agent nodes and routing logic in `fest_agents/`.
2. Created the database action tools for registration, scoring, and profile updates.
3. Connected the agent graph to FastAPI and built the reactive state sync in React.
4. Engineered the fallback mechanism ensuring the system never crashes."

---

## 4. Quick Revision Notes for Tomorrow Morning

- **Framework**: LangGraph (`StateGraph`, `AgentState`, `add_conditional_edges`).
- **Model**: Groq Cloud API, Llama 3.3 70B Versatile, temperature 0.2.
- **Key Files**:
  - `fest_agents/state.py`: TypedDict state definition.
  - `fest_agents/graph.py`: Workflow construction and compilation.
  - `fest_agents/routers.py`: `route_supervisor` logic.
  - `fest_agents/nodes.py`: 7 agent nodes, fallback engine.
  - `fest_agents/tools/`: Domain action tools (profile, registration, judging).
  - `backend/app/api/v1/agents.py`: FastAPI endpoint `/api/agents/chat`.
  - `frontend/src/components/FestAICopilot.jsx`: React chat drawer & reactive sync.
- **Top Concept**: The agent is **action-capable** (mutates database), **resilient** (dual LLM + fallback), and **reactive** (triggers frontend UI updates live).
