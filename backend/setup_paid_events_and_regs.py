import sqlite3
import datetime
import uuid
import hashlib
from app.db.session import SessionLocal
from app.models.event import Event, EventCategory, Venue
from app.models.registration import Registration
from app.models.payment import Payment, Invoice
from app.models.user import User
from app.models.enums import EventStatus, RegistrationStatus, PaymentStatus, UserRole

def setup_mysql():
    print("--- Setting up MySQL college_fest ---")
    db = SessionLocal()
    try:
        # 1. Get or create category & venue
        cat = db.query(EventCategory).filter(EventCategory.name == "Technical").first()
        if not cat:
            cat = EventCategory(name="Technical", slug="technical", description="Coding & Tech Challenges")
            db.add(cat)
            db.flush()

        venue = db.query(Venue).first()
        if not venue:
            venue = Venue(name="Main Tech Block", building="Block B", room="Hall 101", capacity=200)
            db.add(venue)
            db.flush()

        coord = db.query(User).filter(User.role == UserRole.EVENT_COORDINATOR).first()
        coord_id = coord.id if coord else 2

        # 2. Get student user Alex Sharma
        alex = db.query(User).filter(User.id == 1).first()
        if not alex:
            alex = db.query(User).filter(User.role == UserRole.STUDENT).first()
        print(f"Target Student: {alex.full_name} ({alex.email}), ID: {alex.id}")

        # 3. Ensure RoboWars Combat Championship (Paid, ₹150)
        robowars = db.query(Event).filter(Event.title.ilike("%RoboWars%")).first()
        if not robowars:
            robowars = Event(
                title="RoboWars Combat Championship",
                slug="robowars-combat-championship",
                description="Ultimate robot battle arena where custom bots collide.",
                category_id=cat.id,
                coordinator_id=coord_id,
                venue_id=venue.id,
                registration_fee=150.0,
                max_participants=50,
                current_participants=1,
                status=EventStatus.PUBLISHED,
                registration_deadline=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10),
                start_time=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=12),
                end_time=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=12, hours=4),
                is_team_event=False
            )
            db.add(robowars)
            db.flush()
        else:
            robowars.registration_fee = 150.0
            robowars.status = EventStatus.PUBLISHED
            db.flush()
        print(f"RoboWars Event ID: {robowars.id}, Fee: {robowars.registration_fee}")

        # 4. Ensure Algorithm Masters Sprint (Free, ₹0)
        algo = db.query(Event).filter(Event.title.ilike("%Algorithm Masters%")).first()
        if not algo:
            algo = Event(
                title="Algorithm Masters Sprint",
                slug="algorithm-masters-sprint",
                description="Fast-paced algorithmic problem-solving sprint.",
                category_id=cat.id,
                coordinator_id=coord_id,
                venue_id=venue.id,
                registration_fee=0.0,
                max_participants=100,
                current_participants=1,
                status=EventStatus.PUBLISHED,
                registration_deadline=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10),
                start_time=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=11),
                end_time=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=11, hours=3),
                is_team_event=False
            )
            db.add(algo)
            db.flush()
        else:
            algo.registration_fee = 0.0
            algo.status = EventStatus.PUBLISHED
            db.flush()
        print(f"Algorithm Masters Event ID: {algo.id}, Fee: {algo.registration_fee}")

        # 5. Reset Reg ID 3 -> RoboWars Combat Championship (PENDING_PAYMENT, delete any payments)
        reg3 = db.query(Registration).filter(Registration.id == 3).first()
        if not reg3:
            reg3 = Registration(
                id=3,
                registration_number="REG-ROBO-003",
                event_id=robowars.id,
                user_id=alex.id,
                status=RegistrationStatus.PENDING_PAYMENT,
                qr_code_hash=f"PASS-{uuid.uuid4().hex[:12].upper()}"
            )
            db.add(reg3)
            db.flush()
        else:
            reg3.event_id = robowars.id
            reg3.user_id = alex.id
            reg3.status = RegistrationStatus.PENDING_PAYMENT
            # Remove any payments for reg3
            db.query(Payment).filter(Payment.registration_id == 3).delete()
            db.flush()
        print(f"Reg ID 3: Event={reg3.event.title}, Status={reg3.status.value}, Payments count={len(reg3.payments)}")

        # 6. Ensure Alex has a confirmed registration for Algorithm Masters Sprint
        reg_algo = db.query(Registration).filter(
            Registration.event_id == algo.id,
            Registration.user_id == alex.id
        ).first()
        if not reg_algo:
            reg_algo = Registration(
                registration_number="REG-ALGO-101",
                event_id=algo.id,
                user_id=alex.id,
                status=RegistrationStatus.CONFIRMED,
                qr_code_hash=f"PASS-{uuid.uuid4().hex[:12].upper()}"
            )
            db.add(reg_algo)
            db.flush()
        else:
            reg_algo.status = RegistrationStatus.CONFIRMED
            db.flush()
        print(f"Algorithm Masters Reg: ID={reg_algo.id}, Status={reg_algo.status.value}, Pass={reg_algo.qr_code_hash}")

        db.commit()
        print("MySQL successfully updated!")
    finally:
        db.close()


def setup_sqlite():
    print("\n--- Setting up SQLite fest_app.db ---")
    con = sqlite3.connect("fest_app.db")
    cur = con.cursor()

    # Get or create category
    cat_row = cur.execute("SELECT id FROM event_categories WHERE name = 'Technical'").fetchone()
    if not cat_row:
        cur.execute("INSERT INTO event_categories (name, slug, description, created_at, updated_at) VALUES ('Technical', 'technical', 'Tech', datetime('now'), datetime('now'))")
        cat_id = cur.lastrowid
    else:
        cat_id = cat_row[0]

    # Get or create venue
    venue_row = cur.execute("SELECT id FROM venues LIMIT 1").fetchone()
    if not venue_row:
        cur.execute("INSERT INTO venues (name, building, room_number, capacity, is_active, created_at, updated_at) VALUES ('Main Tech Block', 'Block B', 'Hall 101', 200, 1, datetime('now'), datetime('now'))")
        venue_id = cur.lastrowid
    else:
        venue_id = venue_row[0]

    # Ensure user 1 exists
    user1 = cur.execute("SELECT id, email FROM users WHERE id = 1").fetchone()
    if not user1:
        # Check alex
        user1 = cur.execute("SELECT id, email FROM users WHERE email = 'alex.sharma@college.edu'").fetchone()
        if not user1:
            cur.execute("""INSERT INTO users (id, email, full_name, hashed_password, role, is_active, created_at, updated_at) 
                           VALUES (1, 'alex.sharma@college.edu', 'Alex Sharma', 'hashedpw', 'STUDENT', 1, datetime('now'), datetime('now'))""")
            u_id = 1
        else:
            u_id = user1[0]
    else:
        u_id = 1

    # Ensure RoboWars in SQLite
    cur.execute("DELETE FROM events WHERE title LIKE '%RoboWars%'")
    cur.execute("""INSERT INTO events (title, slug, description, category_id, coordinator_id, venue_id, registration_fee, max_participants, current_participants, status, registration_deadline, start_time, end_time, is_team_event, min_team_size, max_team_size, created_at, updated_at)
                   VALUES ('RoboWars Combat Championship', 'robowars-combat-championship', 'Combat arena', ?, ?, ?, 150.0, 50, 1, 'PUBLISHED', datetime('now', '+10 days'), datetime('now', '+12 days'), datetime('now', '+12 days', '+4 hours'), 0, 1, 1, datetime('now'), datetime('now'))""", (cat_id, u_id, venue_id))
    robo_id = cur.lastrowid

    # Ensure Algorithm Masters in SQLite
    cur.execute("DELETE FROM events WHERE title LIKE '%Algorithm Masters%'")
    cur.execute("""INSERT INTO events (title, slug, description, category_id, coordinator_id, venue_id, registration_fee, max_participants, current_participants, status, registration_deadline, start_time, end_time, is_team_event, min_team_size, max_team_size, created_at, updated_at)
                   VALUES ('Algorithm Masters Sprint', 'algorithm-masters-sprint', 'Sprint challenge', ?, ?, ?, 0.0, 100, 1, 'PUBLISHED', datetime('now', '+10 days'), datetime('now', '+11 days'), datetime('now', '+11 days', '+3 hours'), 0, 1, 1, datetime('now'), datetime('now'))""", (cat_id, u_id, venue_id))
    algo_id = cur.lastrowid

    # Reset Reg ID 3 in SQLite
    cur.execute("DELETE FROM registrations WHERE id = 3")
    cur.execute("DELETE FROM payments WHERE registration_id = 3")
    cur.execute("""INSERT INTO registrations (id, registration_number, event_id, user_id, status, registered_at, qr_code_hash, created_at, updated_at)
                   VALUES (3, 'REG-ROBO-003', ?, ?, 'PENDING_PAYMENT', datetime('now'), 'PASS-ROBO-LOCKED-003', datetime('now'), datetime('now'))""", (robo_id, u_id))

    # Add Algorithm Masters registration for user
    cur.execute("DELETE FROM registrations WHERE event_id = ? AND user_id = ?", (algo_id, u_id))
    cur.execute("""INSERT INTO registrations (registration_number, event_id, user_id, status, registered_at, qr_code_hash, created_at, updated_at)
                   VALUES ('REG-ALGO-101', ?, ?, 'CONFIRMED', datetime('now'), 'PASS-ALGO-UNLOCKED-101', datetime('now'), datetime('now'))""", (algo_id, u_id))

    con.commit()
    con.close()
    print("SQLite successfully updated!")

if __name__ == "__main__":
    setup_mysql()
    setup_sqlite()
