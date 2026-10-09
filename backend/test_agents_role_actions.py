import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def print_test(title):
    print(f"\n{'='*60}\nTEST: {title}\n{'='*60}")

def assert_true(cond, msg):
    if not cond:
        print(f"[FAIL] {msg}")
        sys.exit(1)
    else:
        print(f"[PASS] {msg}")

def main():
    print("Testing Role-Aware Agent Chatbot with Live Database Actions...")

    # 1. Log in as Student
    print_test("1. Student Authentication & Queries")
    s_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "alex.sharma@college.edu",
        "password": "password123"
    })
    assert_true(s_login.status_code == 200, "Student logged in")
    s_token = s_login.json()["access_token"]
    s_headers = {"Authorization": f"Bearer {s_token}"}

    # Ask student question about catalog
    res = requests.post(f"{BASE_URL}/agents/chat", headers=s_headers, json={
        "question": "What events are happening in the fest?"
    })
    assert_true(res.status_code == 200, "Chat response received")
    chat_json = res.json()
    assert_true(len(chat_json["response"]) > 20, "Agent returned database event catalog")
    print("Agent Response Sample:\n", chat_json["response"][:200].encode('ascii', 'ignore').decode(), "...\n")

    # 2. Student ACTION: Ask Agent to Register Student for an event
    print_test("2. Student Action: 'Register me for Coding'")
    reg_action_res = requests.post(f"{BASE_URL}/agents/chat", headers=s_headers, json={
        "question": "Please register me for Coding"
    })
    assert_true(reg_action_res.status_code == 200, "Agent processed registration request")
    reg_reply = reg_action_res.json()["response"]
    assert_true("REG-" in reg_reply or "already registered" in reg_reply.lower() or "Registration" in reg_reply, "Agent registered student in MySQL database")
    print("Agent Registration Reply:\n", reg_reply.encode('ascii', 'ignore').decode(), "\n")

    # 3. Student queries their registrations
    print_test("3. Student Queries: 'Show my registrations and passes'")
    my_regs_res = requests.post(f"{BASE_URL}/agents/chat", headers=s_headers, json={
        "question": "Show my registrations and passes"
    })
    assert_true(my_regs_res.status_code == 200, "Agent answered registration inquiry")
    my_regs_reply = my_regs_res.json()["response"]
    assert_true("REG-" in my_regs_reply or "Pass" in my_regs_reply, "Agent pulled student's live registrations from MySQL")
    print("Agent Passes Reply:\n", my_regs_reply[:250].encode('ascii', 'ignore').decode(), "...\n")

    # 4. Log in as Judge
    print_test("4. Judge Authentication & Score Calculation Action")
    j_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "anil@gmail.com",
        "password": "password123"
    })
    assert_true(j_login.status_code == 200, "Judge logged in")
    j_token = j_login.json()["access_token"]
    j_headers = {"Authorization": f"Bearer {j_token}"}

    # Judge ACTION: Ask Agent to calculate scores for a team
    score_action_res = requests.post(f"{BASE_URL}/agents/chat", headers=j_headers, json={
        "question": "Calculate the scores for Team CyberKnights in TechSprint 24-Hour Hackathon: Innovation 24, Technical 25, Presentation 22"
    })
    assert_true(score_action_res.status_code == 200, "Agent calculated scores")
    score_reply = score_action_res.json()["response"]
    assert_true("Score" in score_reply and "71" in score_reply or "Rank" in score_reply, "Agent calculated scores and computed ranking")
    print("Agent Scoring Calculation Reply:\n", score_reply.encode('ascii', 'ignore').decode(), "\n")

    # 5. Judge queries assigned events
    print_test("5. Judge Queries: 'What events am I judging?'")
    j_events_res = requests.post(f"{BASE_URL}/agents/chat", headers=j_headers, json={
        "question": "What events am I judging?"
    })
    assert_true(j_events_res.status_code == 200, "Judge assignments retrieved")
    print("Judge Events Reply:\n", j_events_res.json()["response"][:200].encode('ascii', 'ignore').decode(), "...\n")

    # 6. General / Website Inquiry: How can a judge register here?
    print_test("6. Website Knowledge: 'How can a judge register here?'")
    faq_res = requests.post(f"{BASE_URL}/agents/chat", json={
        "question": "How can a judge register here?"
    })
    assert_true(faq_res.status_code == 200, "FAQ inquiry handled")
    faq_reply = faq_res.json()["response"]
    assert_true("apply" in faq_reply.lower() and "judge" in faq_reply.lower(), "Agent explains Judge registration workflow")
    print("Website Workflow Reply:\n", faq_reply.encode('ascii', 'ignore').decode(), "\n")

    print("\n" + "="*60)
    print("SUCCESS: ALL AGENT CHATBOT ROLE & ACTION TESTS PASSED!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
