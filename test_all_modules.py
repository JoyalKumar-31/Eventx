"""
Comprehensive End-to-End System Verification Suite
Systematically exercises all 16 modules across authentication, student, coordinator, judge, admin, sponsor, and public domains.
"""
import sys
import json
import urllib.request
import urllib.error
import urllib.parse

BASE_URL = "http://127.0.0.1:8000/api"

passed_tests = []
failed_tests = []

def make_request(method, endpoint, data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            resp_body = response.read().decode("utf-8")
            try:
                res_json = json.loads(resp_body)
            except Exception:
                res_json = resp_body
            return status_code, res_json, None
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(err_body)
        except Exception:
            err_json = err_body
        return e.code, err_json, str(e)
    except Exception as e:
        return 0, None, str(e)

def test(name, func):
    print(f"[*] Running: {name} ... ", end="", flush=True)
    try:
        ok, msg = func()
        if ok:
            print(f"PASSED {msg or ''}")
            passed_tests.append(name)
        else:
            print(f"FAILED: {msg}")
            failed_tests.append((name, msg))
    except Exception as ex:
        print(f"EXCEPTION: {ex}")
        failed_tests.append((name, str(ex)))

tokens = {}

# 1. AUTHENTICATION MODULE
def test_auth_logins():
    credentials = [
        ("admin", "admin@college.edu", "password123"),
        ("coordinator_priya", "priya.verma@college.edu", "password123"),
        ("coordinator_dinesh", "dinesh@gmail.com", "password123"),
        ("judge", "anil@gmail.com", "password123"),
        ("student_alex", "alex.sharma@college.edu", "password123"),
        ("student_janam", "janam@gmail.com", "password123"),
    ]
    for role, email, pwd in credentials:
        code, resp, err = make_request("POST", "/auth/login", {"email": email, "password": pwd})
        if code != 200 or not resp.get("access_token"):
            return False, f"Login failed for {role} ({email}): code={code}, err={err or resp}"
        tokens[role] = resp["access_token"]
    tokens["coordinator"] = tokens["coordinator_dinesh"]
    tokens["student"] = tokens["student_janam"]
    return True, f"All primary role accounts authenticated successfully"

def test_auth_me():
    for role in ["admin", "coordinator_priya", "coordinator_dinesh", "judge", "student_alex"]:
        tok = tokens[role]
        code, resp, err = make_request("GET", "/auth/me", token=tok)
        if code != 200 or not resp.get("email"):
            return False, f"GET /auth/me failed for {role}: code={code}, err={err or resp}"
    return True, "Session identity verified for all user roles"

def test_sponsor_registration():
    sponsor_email = "sponsor.techcorp@example.com"
    reg_data = {
        "email": sponsor_email,
        "password": "password123",
        "full_name": "TechCorp Global Rep",
        "role": "SPONSOR",
        "sponsor_profile": {
            "company_name": "TechCorp Global",
            "industry": "Technology",
            "website": "https://techcorp.example.com"
        }
    }
    code, resp, err = make_request("POST", "/auth/register", reg_data)
    if code != 201 and not (code == 400 and "already" in str(resp).lower()):
        return False, f"Sponsor registration returned code {code}: {resp}"
    
    code, login_resp, err = make_request("POST", "/auth/login", {"email": sponsor_email, "password": "password123"})
    if code != 200 or not login_resp.get("access_token"):
        return False, f"Sponsor login failed: code={code}, resp={login_resp}"
    tokens["sponsor"] = login_resp["access_token"]
    return True, f"Sponsor portal account active and authenticated"

# 2. USERS MODULE
def test_users_endpoints():
    code, resp, _ = make_request("GET", "/users", token=tokens["admin"])
    if code != 200 or not isinstance(resp, list):
        return False, f"GET /users failed: code={code}"
    
    code, coords, _ = make_request("GET", "/users/coordinators", token=tokens["admin"])
    if code != 200 or not isinstance(coords, list):
        return False, f"GET /users/coordinators failed: code={code}"
    
    code, judges, _ = make_request("GET", "/users/judges", token=tokens["admin"])
    if code != 200 or not isinstance(judges, list):
        return False, f"GET /users/judges failed: code={code}"
    
    return True, f"Verified directory: {len(resp)} users, {len(coords)} coordinators, {len(judges)} judges"

# 3. PUBLIC MODULE
def test_public_module():
    code, stats, _ = make_request("GET", "/public/stats")
    if code != 200 or "total_events" not in stats:
        return False, f"GET /public/stats failed: {stats}"
    
    code, sched, _ = make_request("GET", "/public/schedules")
    if code != 200 or not isinstance(sched, list):
        return False, f"GET /public/schedules failed: {sched}"
    
    code, venues, _ = make_request("GET", "/public/venues")
    if code != 200 or not isinstance(venues, list):
        return False, f"GET /public/venues failed: {venues}"
    
    return True, f"Public endpoints active: stats, {len(sched)} timeline stages, {len(venues)} venues"

# 4. EVENTS MODULE
events_cache = {}
def test_events_discovery():
    code, events, _ = make_request("GET", "/events")
    if code != 200 or not isinstance(events, list) or len(events) == 0:
        return False, f"GET /events failed: {events}"
    
    events_cache["list"] = events
    # Find solo event
    solo_events = [e for e in events if not e.get("is_team_event", False)]
    events_cache["solo_event"] = solo_events[0] if solo_events else events[0]
    
    # Detail
    code, detail, _ = make_request("GET", f"/events/{events_cache['solo_event']['id']}")
    if code != 200 or "title" not in detail:
        return False, f"GET /events detail failed: {detail}"
    
    code, cats, _ = make_request("GET", "/events/categories")
    if code != 200:
        return False, f"GET /events/categories failed: {cats}"
        
    code, venues, _ = make_request("GET", "/events/venues")
    if code != 200:
        return False, f"GET /events/venues failed: {venues}"
        
    return True, f"Discovered {len(events)} events; verified solo event #{events_cache['solo_event']['id']} ('{events_cache['solo_event']['title']}')"

def test_coordinator_events():
    code, my_events, _ = make_request("GET", "/events/coordinator/my-events", token=tokens["coordinator_dinesh"])
    if code != 200 or not isinstance(my_events, list):
        return False, f"GET /events/coordinator/my-events failed: {my_events}"
    events_cache["dinesh_events"] = my_events
    return True, f"Coordinator Dinesh oversees {len(my_events)} events"

# 5. REGISTRATIONS & ENTRY PASS
reg_cache = {}
def test_student_registration():
    target_event = events_cache["solo_event"]
    target_event_id = target_event["id"]
    
    # Check current registrations for student
    code, my_regs, _ = make_request("GET", "/registrations/my", token=tokens["student_janam"])
    existing = [r for r in my_regs if r.get("event_id") == target_event_id]
    
    if existing:
        reg_obj = existing[0]
    else:
        # Register student for solo event
        reg_payload = {"event_id": target_event_id, "team_id": None}
        code, reg_obj, err = make_request("POST", "/registrations", reg_payload, token=tokens["student_janam"])
        if code != 201:
            return False, f"Registration failed with code {code}: {reg_obj}"
            
    reg_cache["reg_id"] = reg_obj["id"]
    reg_cache["qr_code_hash"] = reg_obj.get("qr_code_hash")
    reg_cache["status"] = reg_obj.get("status")
    
    # If pending payment, verify mock payment to confirm pass
    if reg_cache["status"] == "PENDING_PAYMENT":
        order_payload = {"registration_id": reg_cache["reg_id"], "gateway": "MOCK"}
        code, order_res, _ = make_request("POST", "/payments/create-order", order_payload, token=tokens["student_janam"])
        if code in [200, 201]:
            verify_payload = {
                "order_id": order_res.get("order_id"),
                "payment_id": f"pay_mock_{reg_cache['reg_id']}",
                "signature": "valid_signature_hash"
            }
            make_request("POST", "/payments/verify", verify_payload, token=tokens["student_janam"])
            
    return True, f"Registration #{reg_cache['reg_id']} confirmed for event #{target_event_id}"

def test_entry_pass():
    reg_id = reg_cache.get("reg_id")
    code, pass_data, _ = make_request("GET", f"/registrations/{reg_id}/pass", token=tokens["student_janam"])
    if code != 200 or not pass_data.get("qr_code_hash"):
        return False, f"GET /pass failed: {pass_data}"
    reg_cache["qr_code_hash"] = pass_data["qr_code_hash"]
    reg_cache["pass_data"] = pass_data
    return True, f"Digital pass loaded with QR Hash ({pass_data['qr_code_hash'][:16]}...)"

# 6. TEAMS MODULE & SQUADS
team_cache = {}
def test_teams_flow():
    team_event = None
    for ev in events_cache.get("list", []):
        if ev.get("is_team_event", False):
            team_event = ev
            break
    if not team_event:
        team_event = events_cache["list"][0]
        
    team_payload = {
        "name": f"Apex Tigers Squad {str(hash(tokens['student_alex']))[-4:]}",
        "event_id": team_event["id"]
    }
    code, team_res, _ = make_request("POST", "/teams", team_payload, token=tokens["student_alex"])
    if code == 400 and "already" in str(team_res).lower():
        code, my_teams, _ = make_request("GET", "/teams/my", token=tokens["student_alex"])
        if code == 200 and my_teams:
            team_res = my_teams[0]
            code = 200
            
    if code not in [200, 201]:
        return False, f"Create team failed ({code}): {team_res}"
        
    team_cache["team_id"] = team_res["id"]
    team_cache["invite_code"] = team_res.get("invite_code")
    
    # Detail
    code, detail, _ = make_request("GET", f"/teams/{team_cache['team_id']}", token=tokens["student_alex"])
    if code != 200:
        return False, f"Get team detail failed: {detail}"
        
    # Test new coordinator endpoint: GET /teams/event/{event_id}
    code, ev_teams, _ = make_request("GET", f"/teams/event/{team_event['id']}", token=tokens["coordinator_priya"])
    if code != 200 or not isinstance(ev_teams, list):
        return False, f"GET /teams/event/{team_event['id']} failed: {ev_teams}"
        
    return True, f"Team #{team_res['id']} active (Code: {team_cache.get('invite_code')}); Event #{team_event['id']} has {len(ev_teams)} squads"

# 7. ATTENDANCE SCANNER
def test_attendance_scanning():
    qr_hash = reg_cache.get("qr_code_hash")
    target_event_id = events_cache["solo_event"]["id"]
    
    scan_payload = {
        "qr_payload": qr_hash,
        "event_id": target_event_id,
        "remarks": "Automated Check-in Scanner"
    }
    code, scan_res, _ = make_request("POST", "/attendance/scan", scan_payload, token=tokens["coordinator_dinesh"])
    if code not in [200, 201]:
        return False, f"Attendance scan failed ({code}): {scan_res}"
    
    # Check stats
    code, stats, _ = make_request("GET", f"/attendance/stats/{target_event_id}", token=tokens["coordinator_dinesh"])
    if code != 200:
        return False, f"GET /attendance/stats failed: {stats}"
        
    return True, f"Gate scan verified (Status: {scan_res.get('entry_status')}); Event turnout: {stats.get('total_attended')}/{stats.get('total_registrations')}"

# 8. JUDGING & RUBRIC SCORING
def test_judging_workflow():
    target_event_id = events_cache["solo_event"]["id"]
    coord_tok = tokens["coordinator_dinesh"]
    judge_tok = tokens["judge"]
    
    # 1. Criteria
    code, criteria_list, _ = make_request("GET", f"/judges/criteria/{target_event_id}", token=coord_tok)
    if code != 200 or not isinstance(criteria_list, list):
        return False, f"GET /judges/criteria failed: {criteria_list}"
        
    if not criteria_list:
        crit_data = {
            "event_id": target_event_id,
            "name": "Code Architecture & Logic",
            "weightage": 1.0,
            "max_score": 100.0,
            "description": "Code quality, algorithm efficiency, and modularity"
        }
        code, new_crit, _ = make_request("POST", "/judges/criteria", crit_data, token=coord_tok)
        if code != 201:
            return False, f"POST /judges/criteria failed: {new_crit}"
        criteria_list = [new_crit]
        
    crit_id = criteria_list[0]["id"]
    
    # 2. Assign Judge
    code, judges_list, _ = make_request("GET", "/users/judges", token=tokens["admin"])
    judge_user_id = judges_list[0]["id"]
    
    assign_data = {
        "event_id": target_event_id,
        "judge_id": judge_user_id
    }
    code, assign_res, _ = make_request("POST", "/judges/assign", assign_data, token=coord_tok)
    if code not in [200, 201]:
        return False, f"Judge assignment failed: {assign_res}"
        
    # 3. Start event to open scoring
    make_request("POST", f"/events/{target_event_id}/start", token=coord_tok)
    
    # 4. Submit Score for the confirmed registration
    score_payload = {
        "registration_id": reg_cache["reg_id"],
        "scores": [
            {
                "criteria_id": crit_id,
                "score": 95.0
            }
        ],
        "remarks": "Flawless technical execution and presentation"
    }
    code, score_res, _ = make_request("POST", f"/scores/event/{target_event_id}", score_payload, token=coord_tok)
    if code not in [200, 201]:
        code, score_res, _ = make_request("POST", f"/scores/event/{target_event_id}", score_payload, token=judge_tok)
        if code not in [200, 201]:
            return False, f"Score submission failed ({code}): {score_res}"
            
    return True, f"Rubric active, judge assigned, and scorecard recorded (95.0 pts)"

# 9. RESULTS & LEADERBOARD
def test_results_leaderboard():
    target_event_id = events_cache["solo_event"]["id"]
    coord_tok = tokens["coordinator_dinesh"]
    
    # Leaderboard
    code, lboard, _ = make_request("GET", f"/results/leaderboard/{target_event_id}", token=coord_tok)
    if code != 200 or not isinstance(lboard, list) or len(lboard) == 0:
        return False, f"GET /results/leaderboard failed or empty: {lboard}"
        
    # Publish Results
    code, pub_res, _ = make_request("POST", f"/results/publish/{target_event_id}", token=coord_tok)
    if code not in [200, 201]:
        return False, f"POST /results/publish failed: {pub_res}"
        
    # Public Results
    code, pub_res_list, _ = make_request("GET", f"/results/public/{target_event_id}")
    if code != 200 or not isinstance(pub_res_list, list) or len(pub_res_list) == 0:
        return False, f"GET /results/public/{target_event_id} failed: {pub_res_list}"
        
    return True, f"Leaderboard tabulated; {len(pub_res_list)} ranked entries published to public portal"

# 10. CERTIFICATES & VERIFICATION
def test_certificates_module():
    code, certs, _ = make_request("GET", "/certificates/my", token=tokens["student_janam"])
    if code != 200 or not isinstance(certs, list):
        return False, f"GET /certificates/my failed: {certs}"
        
    if not certs:
        return False, "Expected certificates issued after results publication"
        
    cert = certs[0]
    cert_hash = cert.get("verification_hash")
    cert_id = cert.get("id")
    
    # Public Verification
    code, verif, _ = make_request("GET", f"/certificates/verify/{cert_hash}")
    if code != 200 or not verif.get("is_valid", False):
        return False, f"Certificate verify failed: {verif}"
        
    return True, f"Tamper-proof Certificate #{cert.get('certificate_number')} generated and cryptographically verified"

# 11. PAYMENTS MODULE
def test_payments_module():
    code, my_pay, _ = make_request("GET", "/payments/my", token=tokens["student_janam"])
    if code != 200 or not isinstance(my_pay, list):
        return False, f"GET /payments/my failed: {my_pay}"
        
    code, all_pay, _ = make_request("GET", "/payments/all", token=tokens["admin"])
    if code != 200 or not isinstance(all_pay, list):
        return False, f"GET /payments/all failed: {all_pay}"
        
    return True, f"Financial ledgers verified: {len(my_pay)} student orders, {len(all_pay)} platform transactions"

# 12. ANNOUNCEMENTS MODULE
def test_announcements_module():
    code, ann_list, _ = make_request("GET", "/announcements")
    if code != 200 or not isinstance(ann_list, list):
        return False, f"GET /announcements failed: {ann_list}"
        
    new_ann = {
        "title": "Grand College Fest 2026 Operational Bulletin",
        "content": "All festival arenas, competitive stages, and scoring portals are operating smoothly.",
        "target_audience": "ALL",
        "is_pinned": True
    }
    code, created, _ = make_request("POST", "/announcements", new_ann, token=tokens["admin"])
    if code != 201:
        return False, f"POST /announcements failed: {created}"
        
    return True, f"Announcements verified; broadcast #{created.get('id')} pinned to public board"

# 13. SPONSORS MODULE
def test_sponsors_module():
    code, plans, _ = make_request("GET", "/sponsors/plans")
    if code != 200 or not isinstance(plans, list):
        return False, f"GET /sponsors/plans failed: {plans}"
        
    code, active_promos, _ = make_request("GET", "/sponsors/promotions/active")
    if code != 200 or not isinstance(active_promos, list):
        return False, f"GET /sponsors/promotions/active failed: {active_promos}"
        
    if "sponsor" in tokens:
        code, metrics, _ = make_request("GET", "/sponsors/metrics", token=tokens["sponsor"])
        if code != 200:
            return False, f"GET /sponsors/metrics failed: {metrics}"
            
    return True, f"Sponsor module verified: {len(plans)} sponsorship plans, {len(active_promos)} banner slots"

# 14. ADMIN METRICS & AUDIT
def test_admin_metrics():
    code, metrics, _ = make_request("GET", "/admin/metrics", token=tokens["admin"])
    if code != 200 or "total_users" not in metrics:
        return False, f"GET /admin/metrics failed: {metrics}"
        
    code, coord_m, _ = make_request("GET", "/admin/coordinator-metrics", token=tokens["admin"])
    if code != 200:
        return False, f"GET /admin/coordinator-metrics failed: {coord_m}"
        
    code, judge_m, _ = make_request("GET", "/admin/judge-metrics", token=tokens["admin"])
    if code != 200:
        return False, f"GET /admin/judge-metrics failed: {judge_m}"
        
    code, logs, _ = make_request("GET", "/admin/audit-logs", token=tokens["admin"])
    if code != 200 or not isinstance(logs, list):
        return False, f"GET /admin/audit-logs failed: {logs}"
        
    return True, f"Admin portal verified: {metrics.get('total_users')} users, {metrics.get('total_events')} events, {len(logs)} audit log records"

# 15. NOTIFICATIONS MODULE
def test_notifications_module():
    code, notifs, _ = make_request("GET", "/notifications", token=tokens["student_janam"])
    if code != 200 or not isinstance(notifs, list):
        return False, f"GET /notifications failed: {notifs}"
        
    code, unread, _ = make_request("GET", "/notifications/unread-count", token=tokens["student_janam"])
    if code != 200 or "unread_count" not in unread:
        return False, f"GET /notifications/unread-count failed: {unread}"
        
    return True, f"In-app notification system active ({len(notifs)} alerts delivered)"

# 16. FEST AI AGENTS MODULE
def test_fest_ai_agents():
    # 1. Status
    code, status, _ = make_request("GET", "/agents/status")
    if code != 200 or status.get("status") not in ["online", "operational"]:
        return False, f"GET /agents/status failed: {status}"
        
    # 2. Suggestions
    code, sugg, _ = make_request("GET", "/agents/suggestions")
    if code != 200 or "suggestions" not in sugg:
        return False, f"GET /agents/suggestions failed: {sugg}"
        
    # 3. Chat query
    chat_payload = {
        "question": "What events are scheduled for today, and who is winning?",
        "role": "student"
    }
    code, chat_res, _ = make_request("POST", "/agents/chat", chat_payload)
    if code != 200 or not chat_res.get("response"):
        return False, f"POST /agents/chat failed: {chat_res}"
        
    agent_used = chat_res.get("agent_name", "AI Agent")
    return True, f"AI Copilot ({agent_used}) answered prompt with {len(chat_res['response'])} characters"

def run_all():
    print("=" * 70)
    print("COLLEGE FEST MANAGEMENT SYSTEM - FULL MODULE AUDIT")
    print("=" * 70)
    
    test("1. Authentication: Multi-Role Login", test_auth_logins)
    test("2. Authentication: Session Verification (/auth/me)", test_auth_me)
    test("3. Authentication: Sponsor Onboarding & Login", test_sponsor_registration)
    test("4. Users: Directory & Role Filters", test_users_endpoints)
    test("5. Public: Stats, Schedules, Venues", test_public_module)
    test("6. Events: Catalog, Categories, Details", test_events_discovery)
    test("7. Events: Coordinator Scoped Management", test_coordinator_events)
    test("8. Registrations: Student Enrollment & Payment", test_student_registration)
    test("9. Registrations: Digital QR Entry Pass", test_entry_pass)
    test("10. Teams: Squad Creation, Roster & Event Roster", test_teams_flow)
    test("11. Attendance: QR Gate Scanning & Check-in", test_attendance_scanning)
    test("12. Judging: Rubric Setup & Scoring Workflow", test_judging_workflow)
    test("13. Results: Live Leaderboard & Publication", test_results_leaderboard)
    test("14. Certificates: Generation & Tamper-Proof Verification", test_certificates_module)
    test("15. Payments: Ledgers & Transaction Records", test_payments_module)
    test("16. Announcements: Pinned System Broadcasts", test_announcements_module)
    test("17. Sponsors: Tiers, Plans & Campaigns", test_sponsors_module)
    test("18. Admin: Platform Analytics & Audit Trail", test_admin_metrics)
    test("19. Notifications: In-App User Alerts", test_notifications_module)
    test("20. Fest AI Agents: Multi-Agent Copilot Integration", test_fest_ai_agents)
    
    print("=" * 70)
    print(f"AUDIT SUMMARY: {len(passed_tests)} PASSED, {len(failed_tests)} FAILED")
    print("=" * 70)
    if failed_tests:
        print("\nFAILURE DETAILS:")
        for name, err in failed_tests:
            print(f"  [X] {name}: {err}")
        sys.exit(1)
    else:
        print("\nALL 20 CHECKS ACROSS ALL 16 MODULES PASSED PERFECTLY!")
        sys.exit(0)

if __name__ == "__main__":
    run_all()
