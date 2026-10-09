"""
nodes.py - Multi-Agent Nodes for EventX College Fest Management System
Powered by Groq API (Llama 3.3 70B) with deep live MySQL database integration,
role-aware execution (Student, Coordinator, Judge, Sponsor, Admin), real-world actions,
and full EventX website knowledge.
"""

import os
import re
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv

from .state import AgentState
from .tools import (
    get_all_events,
    get_event_details,
    check_schedule_clash,
    validate_team_size,
    check_registration_status,
    verify_qr_entry_pass,
    register_student_for_event,
    get_user_registrations,
    check_in_participant,
    get_evaluation_rubric,
    calculate_rankings,
    get_live_event_results,
    calculate_and_record_scores,
    get_judge_assigned_events,
    get_fest_analytics,
    get_sponsor_reports,
    generate_certificate_text,
    draft_announcement
)

# Load environment variables
load_dotenv()

_llm_instance = None


def get_llm():
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key and not groq_api_key.startswith("gsk_your_groq_api_key") and len(groq_api_key) > 10:
        try:
            from langchain_groq import ChatGroq
            _llm_instance = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.2,
                api_key=groq_api_key
            )
            return _llm_instance
        except Exception:
            return None
    return None


def invoke_llm(prompt: str, agent_type: str, state: AgentState) -> str:
    """
    Invokes Groq Llama 3.3 70B if available.
    If Groq API key is not configured or network error occurs,
    uses high-quality database-grounded rule-based response generation.
    """
    llm = get_llm()
    if llm:
        try:
            response = llm.invoke(prompt)
            content = response.content.strip()
            if content.startswith("```"):
                content = content.strip("`").strip()
            return content
        except Exception:
            pass

    return _generate_fallback(agent_type, state)


# =====================================================================
# QUERY PARSERS & HELPERS
# =====================================================================

def parse_score_inputs(text: str) -> Tuple[Optional[str], Optional[str], Dict[str, float]]:
    """
    Extracts event name, team name, and criteria scores from natural language judge queries.
    Examples:
      - "calculate the scores for Team Alpha in Hackathon: Innovation 24, Technical 25, Presentation 22"
      - "calculate scores for CyberKnights: 25, 24, 20"
      - "give score 85 to team 1 in codesprint"
    """
    clean = text.strip()

    # 1. Extract criteria score pairs like "Innovation: 24" or "Technical = 25"
    criteria_matches = re.findall(r'([a-zA-Z\s]{3,25})[:=]\s*(\d+(?:\.\d+)?)', clean)
    scores_dict: Dict[str, float] = {}

    if criteria_matches:
        for crit, val in criteria_matches:
            c_name = crit.strip().title()
            if c_name.lower() not in ["for", "in", "at", "score", "scores", "event"]:
                scores_dict[c_name] = float(val)

    # 2. If no criteria pairs, extract isolated numbers (e.g. "scores: 25, 24, 22")
    if not scores_dict:
        # Find all numbers preceded by score/scores or in commas
        num_matches = re.findall(r'\b(\d+(?:\.\d+)?)\b', clean)
        # Filter out numbers that look like years (2026) or IDs (101)
        valid_nums = [float(n) for n in num_matches if float(n) <= 100 and float(n) > 0 and n != "2026"]
        if len(valid_nums) >= 2:
            default_criteria = ["Innovation & Idea", "Technical Implementation", "Presentation & UI", "Q&A Defense"]
            for i, num in enumerate(valid_nums):
                c_name = default_criteria[i] if i < len(default_criteria) else f"Criterion #{i+1}"
                scores_dict[c_name] = num
        elif len(valid_nums) == 1:
            scores_dict["Overall Performance Score"] = valid_nums[0]

    # Default fallback if judge asks to calculate without specifying numbers
    if not scores_dict:
        scores_dict = {
            "Innovation & Originality": 24.0,
            "Technical Execution": 25.0,
            "Presentation & Impact": 23.0
        }

    # 3. Extract Team Name or ID
    team_match = re.search(r'\b(?:team|squad|participant|entry)\s+([a-zA-Z0-9_\-]+(?:\s+[a-zA-Z0-9_\-]+)?)', clean, re.IGNORECASE)
    team_name = team_match.group(1).strip() if team_match else None
    if not team_name:
        reg_match = re.search(r'\b(REG-[0-9a-zA-Z\-]+)\b', clean, re.IGNORECASE)
        team_name = reg_match.group(1).strip() if reg_match else "Team Alpha"

    # 4. Extract Event Name
    event_match = re.search(r'\b(?:in|for|of)\s+([a-zA-Z0-9\s\-]+?)(?::|\s+with|\s+scores|\.|$)', clean, re.IGNORECASE)
    event_name = None
    if event_match:
        potential = event_match.group(1).strip()
        if len(potential) > 3 and not potential.lower().startswith("team"):
            event_name = potential

    return event_name, team_name, scores_dict


def parse_registration_target(text: str) -> Optional[str]:
    """
    Extracts target event name from registration requests like:
      - "register me for CodeSprint"
      - "I want to register for TechSprint 24-Hour Hackathon"
      - "enroll me into Battle of the Bands"
    """
    lower = text.lower()
    patterns = [
        r'register(?:\s+me)?\s+(?:for|into|in|to)\s+([a-zA-Z0-9\s\-]+)',
        r'enroll(?:\s+me)?\s+(?:for|into|in|to)\s+([a-zA-Z0-9\s\-]+)',
        r'sign(?:\s+me)?\s+up\s+(?:for|into|in|to)\s+([a-zA-Z0-9\s\-]+)',
        r'participate\s+(?:in|for)\s+([a-zA-Z0-9\s\-]+)',
        r'join\s+([a-zA-Z0-9\s\-]+)'
    ]
    for p in patterns:
        m = re.search(p, lower)
        if m:
            candidate = m.group(1).strip()
            # Clean trailing punctuation
            candidate = re.split(r'[,.?!;]', candidate)[0].strip()
            if len(candidate) > 2:
                return candidate

    # Check known event names
    all_evs = get_all_events()
    for ev in all_evs:
        t_low = ev["title"].lower()
        if t_low in lower:
            return ev["title"]

    return None


# =====================================================================
# FALLBACK & ROLE-AWARE RESPONSE GENERATOR
# =====================================================================

def _generate_fallback(agent_type: str, state: AgentState) -> str:
    question = state.get("question", "")
    lower = question.lower()
    raw_role = state.get("user_role", "student")
    role = str(raw_role).lower().strip()
    context = state.get("event_context", {})
    user_name = context.get("user_name")
    user_id = context.get("user_id")
    user_email = context.get("user_email")

    greeting = f"Hello **{user_name}**" if user_name else "Hello"

    # -------------------------------------------------------------
    # 1. SUPERVISOR ROUTING
    # -------------------------------------------------------------
    if agent_type == "supervisor":
        tokens = set(re.findall(r'[a-zA-Z0-9_-]+', lower))

        def has_any(keywords):
            for k in keywords:
                if " " in k:
                    if k in lower:
                        return True
                else:
                    if k in tokens or any(t.startswith(k) for t in tokens):
                        return True
            return False

        if has_any(["how to", "how can", "apply as", "where to apply", "registration process", "sign up", "signup", "register as", "candidacy", "onboard"]):
            return "faq_agent"
        elif has_any(["score", "scores", "judge", "judging", "evaluat", "rubric", "rank", "ranking", "rankings", "leaderboard", "marks"]):
            return "judging_agent"
        elif has_any(["register", "registration", "enroll", "pass", "passes", "qr", "gate", "attendance", "checkin", "check-in", "squad", "team"]):
            return "participant_agent"
        elif has_any(["cert", "certificate", "winner", "winners", "announc", "results"]):
            return "result_cert_agent"
        elif has_any(["sponsor", "sponsors", "analytic", "analytics", "revenue", "footfall", "financial", "funding", "stats"]):
            return "sponsor_analytics_agent"
        elif has_any(["timing", "venue", "schedule", "clash", "rules", "when", "event", "events"]):
            return "event_agent"
        else:
            return "faq_agent"

    # -------------------------------------------------------------
    # 2. EVENT MANAGEMENT AGENT
    # -------------------------------------------------------------
    elif agent_type == "event_agent":
        # Check clash detection
        if "clash" in lower or "conflict" in lower:
            evs = get_all_events()
            if len(evs) >= 2:
                c_res = check_schedule_clash(evs[0]["title"], evs[1]["title"])
                status_txt = "⚠️ Potential Schedule/Venue Clash Detected!" if c_res.get("has_conflict") else "✅ No Schedule or Venue Conflicts Found"
                return (
                    f"### Event Schedule Conflict Analysis\n\n"
                    f"{status_txt}\n\n"
                    f"• **Event 1**: {c_res.get('event_1')}\n"
                    f"• **Event 2**: {c_res.get('event_2')}\n"
                    f"• **Venue Clash**: {'Yes' if c_res.get('venue_clash') else 'No'}\n"
                    f"• **Time Overlap**: {'Yes' if c_res.get('time_clash') else 'No'}\n\n"
                    f"Visit the live [Fest Schedule](/schedule) or [Campus Venues](/venues) for interactive floor maps."
                )

        matched = get_event_details(question)
        if matched:
            rules_str = "\n".join(f"• {r}" for r in matched.get("rules", []))
            fee_val = float(matched.get("registration_fee", 0))
            fee_str = f"₹{fee_val:.0f}" if fee_val > 0 else "Free Entry"
            is_team = matched.get("is_team_event", matched.get("min_team_size", 1) > 1)
            min_s = matched.get("min_team_size", 1)
            max_s = matched.get("max_team_size", 1)
            team_str = f"{min_s}-{max_s} members" if is_team else "Individual (Solo)"
            return (
                f"### 🎯 {matched['title']} ({matched['category']})\n\n"
                f"📍 **Venue**: {matched['venue']}\n"
                f"⏰ **Time**: {matched['start_time']} – {matched['end_time']}\n"
                f"👥 **Team Size**: {team_str}\n"
                f"💰 **Registration Fee**: {fee_str}\n\n"
                f"📋 **Official Competition Rules**:\n{rules_str}\n\n"
                f"💡 *Ready to participate? Just say 'Register me for {matched['title']}'!*"
            )

        all_evs = get_all_events()
        if all_evs:
            events_str = "\n".join(
                f"• **{e['title']}** ({e['category']}) — {e['time']} at *{e['venue']}* [{e['fee']}]"
                for e in all_evs[:6]
            )
            return (
                f"### 🎪 Live EventX Festival Catalog\n\n"
                f"Here are the active competitions and workshops queried from our live database:\n\n"
                f"{events_str}\n\n"
                f"🔍 *Ask for any specific event by name to see complete rules, team sizes, and venue maps!*"
            )

        return "EventX features competitions across Technical, Cultural, and Gaming domains. Explore the complete interactive catalog at [/events](/events)."

    # -------------------------------------------------------------
    # 3. PARTICIPANT & TEAM AGENT (ACTIONS & QUERIES)
    # -------------------------------------------------------------
    elif agent_type == "participant_agent":
        tool_outputs = state.get("tool_outputs") or {}
        if "action_result" in tool_outputs:
            return tool_outputs["action_result"]["message"]

        # ACTION 1: Register student for event
        is_register_intent = any(k in lower for k in ["register me", "register for", "sign me up", "enroll me", "i want to register", "join event"])
        if is_register_intent:
            target_event = parse_registration_target(question)
            if not target_event:
                # If user just said "register me" without event name
                all_evs = get_all_events()
                ev_names = ", ".join(f"**{e['title']}**" for e in all_evs[:4])
                return (
                    f"I would be happy to register you! Which competition would you like to join?\n\n"
                    f"Popular active events: {ev_names}.\n\n"
                    f"Simply say: *'Register me for [Event Name]'*."
                )

            # Execute real registration in database
            reg_result = register_student_for_event(
                event_name_or_id=target_event,
                user_id=user_id,
                user_email=user_email
            )
            return reg_result["message"]

        # ACTION 2: Show my registrations / passes
        if "my_registrations" in tool_outputs or any(k in lower for k in ["my registration", "my registrations", "my pass", "my passes", "what events am i", "my events", "my tickets"]):
            if not user_id and not user_email:
                return (
                    "Please log into your student account to inspect your registrations and digital passes. "
                    "You can sign in at [/login](/login)."
                )

            regs = tool_outputs.get("my_registrations") if "my_registrations" in tool_outputs else get_user_registrations(user_id=user_id, user_email=user_email)
            if not regs:
                return (
                    f"{greeting}! You have not registered for any events yet. "
                    f"Browse the [Event Catalog](/events) or tell me *'Register me for [Event]'* to get started!"
                )

            cards = []
            for r in regs:
                cards.append(
                    f"• **{r['event_title']}**\n"
                    f"  - Reg ID: `{r['registration_number']}` | Status: `{r['status']}`\n"
                    f"  - Schedule: {r['time']} at {r['venue']}\n"
                    f"  - Digital QR Pass: `{r['qr_pass']}`"
                )
            return (
                f"### 🎟️ Your EventX Registrations & Passes\n\n"
                f"{greeting}! Here are your confirmed festival enrollments from our database:\n\n"
                + "\n\n".join(cards)
                + f"\n\nAccess your digital barcoded gate passes anytime in [Student Passes](/student/passes)."
            )

        # ACTION 3: Check-in / Gate Scan
        if "checkin" in lower or "check-in" in lower or "attendance" in lower:
            words = question.upper().split()
            target_reg = None
            for w in words:
                if "REG-" in w or "PASS-" in w:
                    target_reg = w
                    break
            if target_reg:
                res = check_in_participant(target_reg, coordinator_id=user_id)
                return res["message"]

        # Registration status lookup by code
        for w in question.upper().split():
            if "REG-" in w or (w.isdigit() and len(w) <= 4):
                res = check_registration_status(w)
                if res.get("found"):
                    return (
                        f"### 📄 Registration Record: `{res.get('registration_id', w)}`\n\n"
                        f"• **Event**: {res.get('event')}\n"
                        f"• **Team / Competitor**: {res.get('team_name')}\n"
                        f"• **Leader**: {res.get('leader')}\n"
                        f"• **Squad Size**: {res.get('members_count')} members\n"
                        f"• **Status**: `{res.get('payment_status')}`\n"
                        f"• **Digital Pass Key**: `{res.get('qr_pass')}`\n"
                        f"• **Gate Check-In**: **{res.get('attendance')}**"
                    )

        # Gate Pass verification
        for w in question.upper().split():
            if "PASS-" in w:
                res = verify_qr_entry_pass(w)
                status_str = "✅ GRANTED" if res.get("granted") else "❌ DENIED"
                msg = res.get("message") or res.get("reason", "Pass processed.")
                return f"### Gate Pass Verification for `{w}`\n\n**Decision**: {status_str}\n\n{msg}"

        return (
            f"{greeting}! In EventX, students can register individually or in squads. "
            f"You can ask me to **register you directly** for any event (e.g. *'Register me for CodeSprint'*), "
            f"lookup your active passes, or check team size eligibility."
        )

    # -------------------------------------------------------------
    # 4. JUDGING & EVALUATION AGENT (ACTIONS & QUERIES)
    # -------------------------------------------------------------
    elif agent_type == "judging_agent":
        tool_outputs = state.get("tool_outputs") or {}
        if "score_calculation" in tool_outputs:
            calc_res = tool_outputs["score_calculation"]
            breakdown_lines = "\n".join(
                f"• **{item['criteria']}**: `{item['score']} / {item['max']} pts`"
                for item in calc_res["breakdown"]
            )
            db_saved_msg = "✅ **Evaluation permanently recorded into MySQL database.**" if calc_res["saved_to_db"] else "ℹ️ Calculated evaluation scorecard."
            return (
                f"### ⚖️ Judge Scorecard & Leaderboard Calculation\n\n"
                f"• **Event**: {calc_res['event_title']}\n"
                f"• **Evaluated Team / Entry**: **{calc_res['team_name']}** (Reg ID: `{calc_res['registration_id']}`)\n\n"
                f"**Score Breakdown**:\n{breakdown_lines}\n\n"
                f"**Aggregate Score**: `{calc_res['total_score']} / {calc_res['max_score']}` ({calc_res['percentage']}%)\n"
                f"**Current Standing**: 🏆 **Rank #{calc_res['current_rank']}**\n\n"
                f"{db_saved_msg}\n\n"
                f"View all event scorecards in your [Judge Scoring Console](/judge/scoring)."
            )

        # ACTION 1: Calculate and record scores
        is_scoring_intent = any(k in lower for k in ["calculate", "score", "scores", "marks", "grade", "points", "evaluate"])
        has_numbers = bool(re.search(r'\d+', question))

        if is_scoring_intent and has_numbers:
            ev_name, team_name, scores_dict = parse_score_inputs(question)
            calc_res = calculate_and_record_scores(
                event_name_or_id=ev_name or "Event",
                team_or_reg_identifier=team_name or "Team Alpha",
                scores_dict=scores_dict,
                judge_id=user_id if role in ["judge", "admin", "event_coordinator"] else None,
                remarks=f"Evaluated by {user_name or 'Judge'}"
            )

            breakdown_lines = "\n".join(
                f"• **{item['criteria']}**: `{item['score']} / {item['max']} pts`"
                for item in calc_res["breakdown"]
            )

            db_saved_msg = "✅ **Evaluation permanently recorded into MySQL database.**" if calc_res["saved_to_db"] else "ℹ️ Calculated evaluation scorecard."

            return (
                f"### ⚖️ Judge Scorecard & Leaderboard Calculation\n\n"
                f"• **Event**: {calc_res['event_title']}\n"
                f"• **Evaluated Team / Entry**: **{calc_res['team_name']}** (Reg ID: `{calc_res['registration_id']}`)\n\n"
                f"**Score Breakdown**:\n{breakdown_lines}\n\n"
                f"**Aggregate Score**: `{calc_res['total_score']} / {calc_res['max_score']}` ({calc_res['percentage']}%)\n"
                f"**Current Standing**: 🏆 **Rank #{calc_res['current_rank']}**\n\n"
                f"{db_saved_msg}\n\n"
                f"View all event scorecards in your [Judge Scoring Console](/judge/scoring)."
            )

        # ACTION 2: Show my assigned events (Judge role)
        if any(k in lower for k in ["assigned", "my event", "my events", "events i judge", "what do i judge"]):
            if user_id:
                assigned = get_judge_assigned_events(user_id)
                if assigned:
                    lines = []
                    for a in assigned:
                        lines.append(
                            f"• **{a['title']}** ({a['category']})\n"
                            f"  - Venue: {a['venue']} | Time: {a['time']}\n"
                            f"  - Submissions: {a['total_submissions']} total ({a['evaluated_submissions']} evaluated, {a['pending_submissions']} pending)"
                        )
                    return (
                        f"### ⚖️ Your Assigned Judging Competitions\n\n"
                        f"{greeting}! Here are your designated evaluation panels from the database:\n\n"
                        + "\n\n".join(lines)
                        + f"\n\nTo score a submission, tell me *'Calculate scores for [Team] in {assigned[0]['title']}: Innovation 25, Technical 24...'*."
                    )

        # ACTION 3: Show live event rankings / leaderboards
        if any(k in lower for k in ["rank", "ranking", "rankings", "leaderboard", "standing", "standings"]):
            live_standings = get_live_event_results(question)
            if live_standings:
                ev_title = live_standings[0].get("event", "Event")
                stand_lines = "\n".join(
                    f"• **{s['position']}**: {s['team_name']} — Score: **{s['total_score']} pts**"
                    for s in live_standings
                )
                return (
                    f"### 🏆 Live Leaderboard: {ev_title}\n\n"
                    f"Current ranked standings computed from judge evaluations:\n\n"
                    f"{stand_lines}\n\n"
                    f"Full real-time rankings are published at [/results](/results)."
                )

        # Default Judging Rubric
        rubric_data = get_evaluation_rubric("Technical")
        rubric_items = rubric_data.get("rubric", {})
        crit_str = "\n".join(f"• **{name}**: {pts} pts" for name, pts in rubric_items.items())
        return (
            f"### ⚖️ Official EventX Judging Rubric\n\n"
            f"{crit_str}\n\n"
            f"• **Total Scale**: Maximum {rubric_data.get('max_score', 100)} points.\n\n"
            f"As a Judge, you can tell me: *'Calculate scores for Team Alpha in Hackathon: Innovation 24, Technical 25, Presentation 22'* "
            f"and I will automatically compute the weighted percentages, assign leader rankings, and save the marks to the database."
        )

    # -------------------------------------------------------------
    # 5. RESULT & CERTIFICATE AGENT
    # -------------------------------------------------------------
    elif agent_type == "result_cert_agent":
        live_standings = get_live_event_results(question)
        if live_standings:
            winner = live_standings[0]
            cert = generate_certificate_text(winner["team_name"], winner["event"], "1st Place Winner")
            return (
                f"### 🏆 Official Result Announcement\n\n"
                f"• **Event**: {winner['event']}\n"
                f"• **First Place Winner**: **{winner['team_name']}** ({winner['total_score']} pts)\n\n"
                f"📜 **Generated Certificate Credential**:\n"
                f"> \"{cert['certificate_body']}\"\n\n"
                f"• Verification Hash: `{cert['certificate_id']}`\n"
                f"Verify credentials publicly anytime at [/verify-certificate](/verify-certificate)."
            )
        return (
            f"🏆 **EventX Official Results & Digital Credentials**\n\n"
            f"All winners and verified attendees receive tamper-proof cryptographic certificates. "
            f"You can verify any certificate using its QR code hash or ID at [/verify-certificate](/verify-certificate) "
            f"or inspect live competition rankings at [/results](/results)."
        )

    # -------------------------------------------------------------
    # 6. OPERATIONS & ANALYTICS AGENT
    # -------------------------------------------------------------
    elif agent_type == "sponsor_analytics_agent":
        analytics = get_fest_analytics()
        s = analytics["overview"]
        return (
            f"### 📊 EventX Real-Time Festival Analytics\n\n"
            f"• **Registered Students**: {s['total_registered_students']:,}\n"
            f"• **Active Catalog Events**: {s['total_events']}\n"
            f"• **Participant Registration Revenue**: ₹{s['total_revenue_inr']:,}\n"
            f"• **Gate Check-In / Attendance Rate**: {s['checkin_rate_percent']}%\n\n"
            f"Explore comprehensive fiscal breakdowns in the [Financials & Revenue Console](/admin/revenue)."
        )

    # -------------------------------------------------------------
    # 7. FAQ & COMPREHENSIVE WEBSITE HELPDESK
    # -------------------------------------------------------------
    else:
        # Personalized role recommendations
        role_greeting = f"{greeting}! Welcome to EventX."
        role_hints = ""

        if role == "judge":
            role_hints = (
                f"\n\n⚖️ **Judge Actions Available**:\n"
                f"• Ask *'What events am I judging?'* to view your assigned panels.\n"
                f"• Ask *'Calculate scores for [Team]: 25, 24, 22'* to compute scores and update the database.\n"
                f"• Access your full evaluation console at [/judge/scoring](/judge/scoring)."
            )
        elif role == "student":
            role_hints = (
                f"\n\n🎓 **Student Actions Available**:\n"
                f"• Ask *'Register me for [Event Name]'* to register instantly.\n"
                f"• Ask *'Show my registrations'* or *'Show my passes'* to inspect digital passes.\n"
                f"• Access your dashboard at [/student/dashboard](/student/dashboard)."
            )
        elif role == "event_coordinator":
            role_hints = (
                f"\n\n🛡️ **Coordinator Actions Available**:\n"
                f"• Ask *'Check in REG-101'* to mark gate attendance.\n"
                f"• Ask *'Check schedule clash for [Event]'* to inspect overlaps.\n"
                f"• Access your command portal at [/coordinator/dashboard](/coordinator/dashboard)."
            )
        elif role == "admin":
            role_hints = (
                f"\n\n👑 **Admin Console Actions Available**:\n"
                f"• Review pending Coordinator & Judge applications at [/admin/applications](/admin/applications).\n"
                f"• Issue cryptographic Judge invitations at [/admin/applications](/admin/applications).\n"
                f"• View system audit trail at [/admin/audit-logs](/admin/audit-logs)."
            )

        return (
            f"{role_greeting}\n\n"
            f"**EventX Complete Portal Navigation**:\n\n"
            f"• 🎪 **Festival Catalog**: [Browse Events](/events) | [Fest Schedule](/schedule) | [Campus Venues](/venues)\n"
            f"• 🏆 **Live Results**: [Leaderboards & Winners](/results) | [Verify Certificates](/verify-certificate)\n"
            f"• 📢 **Announcements**: [Campus Broadcasts](/announcements)\n\n"
            f"**Account & Registration Workflows**:\n"
            f"• 🎓 **Student Registration**: Public signup at [/register](/register) (strictly assigns Student role).\n"
            f"• 🛡️ **Event Coordinator**: Apply with faculty & experience at [/apply/coordinator](/apply/coordinator) (reviewed & approved by Admin).\n"
            f"• ⚖️ **Fest Judge**: Apply for official judging panel at [/apply/judge](/apply/judge) or redeem invitation token at [/invite/accept](/invite/accept).\n"
            + role_hints
        )


# =====================================================================
# AGENT NODES
# =====================================================================

def supervisor_agent(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    user_role = state.get("user_role", "student")
    history = state.get("history", [])
    attempt = state.get("attempts", 0)

    prompt = f"""
You are the Supervisor Agent of EventX College Fest Management System.

USER ROLE:
{user_role}

USER REQUEST:
{question}

Analyze the request and route to ONLY ONE of the following specialized agents:
- event_agent: Event details, schedules, timings, venues, rules, schedule clashes.
- participant_agent: Event registration, student registration action, team size limits, QR entry pass, gate attendance, my passes.
- judging_agent: Scoring rubrics, judge evaluations, score calculations, calculate marks, team rankings, assigned judging panels.
- result_cert_agent: Publishing results, winner announcements, generating certificate text.
- sponsor_analytics_agent: Fest revenue, participant counts, footfall, sponsor packages and reports.
- faq_agent: Website navigation, registration procedures, roles, campus locations, helpdesk.

Return ONLY the agent name (one of: event_agent, participant_agent, judging_agent, result_cert_agent, sponsor_analytics_agent, faq_agent).
Do not use markdown fences.
"""

    route = invoke_llm(prompt, "supervisor", state).strip().lower()

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


def event_management_agent(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])

    all_events = get_all_events()
    matched_event = get_event_details(question)

    prompt = f"""
You are the Event Management Agent of EventX.
USER INQUIRY: {question}
EVENT DATA: {matched_event or all_events[:5]}
Respond politely with complete event schedules, venue locations, team requirements, and rules.
"""
    answer = invoke_llm(prompt, "event_agent", state)

    new_history = list(history)
    new_history.append("Event Management Agent processed request")

    return {
        "agent_response": answer,
        "tool_outputs": {"matched_event": matched_event},
        "history": new_history,
        "attempts": attempt + 1
    }


def participant_team_agent(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])
    context = state.get("event_context", {})

    tools_context = {}
    lower = question.lower()

    # Pre-execute actions if detected
    if any(k in lower for k in ["register me", "register for", "sign me up", "enroll me", "i want to register", "join event"]):
        target = parse_registration_target(question)
        if target:
            tools_context["action_result"] = register_student_for_event(
                event_name_or_id=target,
                user_id=context.get("user_id"),
                user_email=context.get("user_email")
            )

    if any(k in lower for k in ["my registration", "my registrations", "my pass", "my passes", "what events am i", "my events"]):
        tools_context["my_registrations"] = get_user_registrations(
            user_id=context.get("user_id"),
            user_email=context.get("user_email")
        )

    state["tool_outputs"] = tools_context

    prompt = f"""
You are the Participant and Team Agent of EventX.
USER INQUIRY: {question}
CONTEXT & ACTIONS EXECUTED: {tools_context}
Answer accurately and confirm any registrations or passes.
"""
    answer = invoke_llm(prompt, "participant_agent", state)

    new_history = list(history)
    new_history.append("Participant & Team Agent processed request")

    return {
        "agent_response": answer,
        "tool_outputs": tools_context,
        "history": new_history,
        "attempts": attempt + 1
    }


def judging_evaluation_agent(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])
    context = state.get("event_context", {})

    tools_context = {}
    lower = question.lower()

    if any(k in lower for k in ["calculate", "score", "scores", "marks", "grade", "points", "evaluate"]) and re.search(r'\d+', question):
        ev_name, team_name, scores_dict = parse_score_inputs(question)
        tools_context["score_calculation"] = calculate_and_record_scores(
            event_name_or_id=ev_name or "Event",
            team_or_reg_identifier=team_name or "Team Alpha",
            scores_dict=scores_dict,
            judge_id=context.get("user_id"),
            remarks="Evaluated via Fest AI Judge Copilot"
        )

    if any(k in lower for k in ["assigned", "my event", "my events", "events i judge"]):
        if context.get("user_id"):
            tools_context["assigned_events"] = get_judge_assigned_events(context.get("user_id"))

    state["tool_outputs"] = tools_context

    prompt = f"""
You are the Judging & Evaluation Agent of EventX.
USER INQUIRY: {question}
EVALUATION RESULTS & CONTEXT: {tools_context}
Present detailed marks, weightages, criteria, and leader rankings.
"""
    answer = invoke_llm(prompt, "judging_agent", state)

    new_history = list(history)
    new_history.append("Judging & Evaluation Agent processed request")

    return {
        "agent_response": answer,
        "tool_outputs": tools_context,
        "history": new_history,
        "attempts": attempt + 1
    }


def result_cert_agent(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])

    prompt = f"You are the Result & Certificate Agent of EventX. User question: {question}."
    answer = invoke_llm(prompt, "result_cert_agent", state)

    new_history = list(history)
    new_history.append("Result & Certificate Agent processed request")

    return {
        "agent_response": answer,
        "history": new_history,
        "attempts": attempt + 1
    }


def sponsor_analytics_agent(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])

    analytics = get_fest_analytics()
    prompt = f"You are the Sponsor & Analytics Agent of EventX. User query: {question}. Stats: {analytics}."
    answer = invoke_llm(prompt, "sponsor_analytics_agent", state)

    new_history = list(history)
    new_history.append("Sponsor & Analytics Agent processed request")

    return {
        "agent_response": answer,
        "tool_outputs": analytics,
        "history": new_history,
        "attempts": attempt + 1
    }


def faq_helpdesk_agent(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    attempt = state.get("attempts", 0)
    history = state.get("history", [])

    prompt = f"You are the Campus Helpdesk & Navigation Agent of EventX. User question: {question}."
    answer = invoke_llm(prompt, "faq_agent", state)

    new_history = list(history)
    new_history.append("Campus Helpdesk Agent processed request")

    return {
        "agent_response": answer,
        "history": new_history,
        "attempts": attempt + 1
    }
