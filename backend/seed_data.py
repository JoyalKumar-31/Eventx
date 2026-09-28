"""
Database Seeder for FESTORA
Populates MySQL database with rich, realistic fest data matching the frontend specification.
"""
from datetime import datetime, date, time, timedelta, timezone
import sys
import io

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
import app.models
from app.models.user import User, RoleEnum, UserInterest
from app.models.event import (
    Event, EventCategory, Venue, EventRule, EventRound, EventPrize, EventFAQ, ScheduleItem
)
from app.models.team import Team, TeamMember
from app.models.registration import Registration, RegistrationStatus
from app.models.payment import Payment, Invoice, PaymentStatus
from app.models.pass_attendance import FestPass, PassStatus, Attendance, AttendanceStatus
from app.models.judging import JudgeAssignment, Evaluation, EventResult
from app.models.certificate import Certificate
from app.models.notification import Notification
from app.models.sponsor import Sponsor, SponsorshipPlan, Sponsorship, SponsorPromotion
from app.utils.qr import generate_qr_code_image


def seed_database():
    db: Session = SessionLocal()
    print("🌱 Starting FESTORA database seeding...")

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "admin@festora.com").first():
            print("Database already contains seed data. Skipping duplicate seed.")
            return

        # -------------------------------------------------------------
        # 1. USERS & ROLES
        # -------------------------------------------------------------
        print("  Creating users across all roles...")
        admin_user = User(
            id=1,
            email="admin@festora.com",
            hashed_password=hash_password("admin123"),
            full_name="Alex Rivera",
            phone="+91 98765 00001",
            college="National Institute of Technology",
            department="Faculty Administration",
            role=RoleEnum.ADMIN,
            is_active=True,
            is_verified=True
        )

        coordinator_user = User(
            id=2,
            email="sarah@festora.com",
            hashed_password=hash_password("password123"),
            full_name="Sarah Jenkins",
            phone="+91 98765 00002",
            college="National Institute of Technology",
            department="Computer Science",
            year_of_study=4,
            role=RoleEnum.COORDINATOR,
            is_active=True,
            is_verified=True
        )

        judge_user = User(
            id=3,
            email="dr.sharma@festora.com",
            hashed_password=hash_password("password123"),
            full_name="Dr. Vikram Sharma",
            phone="+91 98765 00003",
            college="Indian Institute of Technology",
            department="AI & Robotics",
            role=RoleEnum.JUDGE,
            is_active=True,
            is_verified=True
        )

        joyal_user = User(
            id=21,  # matches spec id: 21
            email="joyal@festora.com",
            hashed_password=hash_password("password123"),
            full_name="Joyal Kumar",
            phone="+91 98765 43210",
            college="National Institute of Technology",
            department="Computer Science & Engineering",
            year_of_study=3,
            role=RoleEnum.STUDENT,
            is_active=True,
            is_verified=True
        )

        student2 = User(
            id=22,
            email="ananya@festora.com",
            hashed_password=hash_password("password123"),
            full_name="Ananya Roy",
            phone="+91 98765 43211",
            college="BITS Pilani",
            department="Information Technology",
            year_of_study=3,
            role=RoleEnum.STUDENT,
            is_active=True,
            is_verified=True
        )

        student3 = User(
            id=23,
            email="rohit@festora.com",
            hashed_password=hash_password("password123"),
            full_name="Rohit Verma",
            phone="+91 98765 43212",
            college="Delhi Technological University",
            department="Electronics",
            year_of_study=2,
            role=RoleEnum.STUDENT,
            is_active=True,
            is_verified=True
        )

        db.add_all([admin_user, coordinator_user, judge_user, joyal_user, student2, student3])
        db.commit()

        # Joyal's Interests
        db.add_all([
            UserInterest(user_id=joyal_user.id, category="Technical"),
            UserInterest(user_id=joyal_user.id, category="Gaming"),
            UserInterest(user_id=joyal_user.id, category="Workshop"),
        ])
        db.commit()

        # -------------------------------------------------------------
        # 2. VENUES
        # -------------------------------------------------------------
        print("  Creating campus venues...")
        v_lab2 = Venue(
            id=1,
            name="Computer Lab 2",
            building="Turing Computing Block",
            room_number="CL-204",
            capacity=200,
            latitude=10.1234,
            longitude=76.4567,
            map_url="https://maps.google.com/?q=10.1234,76.4567"
        )
        v_audi = Venue(
            id=2,
            name="Main Auditorium",
            building="Dr. APJ Abdul Kalam Convention Center",
            room_number="AUD-01",
            capacity=1200,
            latitude=10.1240,
            longitude=76.4580,
            map_url="https://maps.google.com/?q=10.1240,76.4580"
        )
        v_seminar = Venue(
            id=3,
            name="Seminar Hall 1",
            building="Aryabhata Academic Block",
            room_number="SH-101",
            capacity=300,
            latitude=10.1250,
            longitude=76.4550,
            map_url="https://maps.google.com/?q=10.1250,76.4550"
        )
        v_ground = Venue(
            id=4,
            name="Open Air Amphitheatre",
            building="Cultural Plaza",
            room_number="OAT-G",
            capacity=2500,
            latitude=10.1260,
            longitude=76.4590,
            map_url="https://maps.google.com/?q=10.1260,76.4590"
        )
        db.add_all([v_lab2, v_audi, v_seminar, v_ground])
        db.commit()

        # -------------------------------------------------------------
        # 3. CATEGORIES
        # -------------------------------------------------------------
        print("  Creating categories...")
        cat_tech = EventCategory(id=1, name="Technical", description="Coding, hackathons, robotics, and design challenges", icon="code")
        cat_cult = EventCategory(id=2, name="Cultural", description="Music, dance, drama, and artistic exhibitions", icon="music")
        cat_work = EventCategory(id=3, name="Workshop", description="Hands-on masterclasses from industry leaders", icon="book-open")
        cat_game = EventCategory(id=4, name="Gaming", description="Esports tournaments (Valorant, BGMI, FIFA)", icon="gamepad")
        cat_sport = EventCategory(id=5, name="Sports", description="Inter-college athletic and indoor games", icon="activity")
        db.add_all([cat_tech, cat_cult, cat_work, cat_game, cat_sport])
        db.commit()

        # -------------------------------------------------------------
        # 4. EVENTS
        # -------------------------------------------------------------
        print("  Creating events matching specifications...")
        # Code Sprint - Event ID 14 (Matches user specification prompt)
        event_codesprint = Event(
            id=14,
            name="Code Sprint",
            category_id=cat_tech.id,
            venue_id=v_lab2.id,
            coordinator_id=coordinator_user.id,
            description="Build something extraordinary in a 3-hour intense speed programming showdown.",
            short_description="3-hour algorithmic competitive coding challenge testing data structures and speed.",
            banner_url="https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800",
            registration_fee=150.00,
            capacity=200,
            registered_count=142,
            min_team_size=1,
            max_team_size=1,
            event_date=date(2026, 10, 28),
            start_time=time(10, 0),
            end_time=time(13, 0),
            registration_deadline=datetime(2026, 10, 27, 23, 59),
            status="UPCOMING",
            is_active=True,
            is_featured=True
        )

        # AI Challenge - Event ID 18 (Matches user specification prompt)
        event_ai = Event(
            id=18,
            name="AI Challenge",
            category_id=cat_tech.id,
            venue_id=v_seminar.id,
            coordinator_id=coordinator_user.id,
            description="Develop and evaluate fine-tuned multi-modal AI agents to solve real-world sustainability problems.",
            short_description="Agentic LLM hackathon solving real-world challenges.",
            banner_url="https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800",
            registration_fee=200.00,
            capacity=150,
            registered_count=88,
            min_team_size=2,
            max_team_size=4,
            event_date=date(2026, 10, 29),
            start_time=time(9, 30),
            end_time=time(17, 30),
            registration_deadline=datetime(2026, 10, 28, 20, 0),
            status="UPCOMING",
            is_active=True,
            is_featured=True
        )

        # Hackathon - Event ID 19
        event_hackathon = Event(
            id=19,
            name="ByteHack 2026",
            category_id=cat_tech.id,
            venue_id=v_lab2.id,
            coordinator_id=coordinator_user.id,
            description="24-hour national hackathon building scalable full-stack web and mobile applications.",
            short_description="24-Hour flagship software hackathon.",
            banner_url="https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800",
            registration_fee=300.00,
            capacity=100,
            registered_count=76,
            min_team_size=2,
            max_team_size=4,
            event_date=date(2026, 10, 28),
            start_time=time(14, 0),
            end_time=time(14, 0),
            registration_deadline=datetime(2026, 10, 27, 18, 0),
            status="UPCOMING",
            is_active=True,
            is_featured=True
        )

        # Battle of the Bands - Cultural
        event_bands = Event(
            id=20,
            name="Battle of the Bands",
            category_id=cat_cult.id,
            venue_id=v_ground.id,
            coordinator_id=coordinator_user.id,
            description="The premier collegiate musical face-off showcasing top rock, indie, and fusion bands.",
            short_description="Flagship inter-college music competition under the stars.",
            banner_url="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800",
            registration_fee=500.00,
            capacity=50,
            registered_count=32,
            min_team_size=3,
            max_team_size=8,
            event_date=date(2026, 10, 30),
            start_time=time(18, 0),
            end_time=time(22, 30),
            registration_deadline=datetime(2026, 10, 29, 12, 0),
            status="UPCOMING",
            is_active=True,
            is_featured=True
        )

        db.add_all([event_codesprint, event_ai, event_hackathon, event_bands])
        db.commit()

        # Rules for Code Sprint
        db.add_all([
            EventRule(event_id=14, order=1, rule_text="Individual participation only. No external collaboration allowed."),
            EventRule(event_id=14, order=2, rule_text="Supported languages: C++, Python, Java, JavaScript, Rust."),
            EventRule(event_id=14, order=3, rule_text="Internet access will be restricted to documentation only."),
            EventRule(event_id=14, order=4, rule_text="Plagiarism detection software will run across all submissions.")
        ])

        # Rounds for Code Sprint
        db.add_all([
            EventRound(event_id=14, round_number=1, title="Speed Coding Blitz", description="4 algorithmic problems in 45 minutes", start_time=datetime(2026, 10, 28, 10, 0)),
            EventRound(event_id=14, round_number=2, title="Complex Data Structures Challenge", description="3 hard dynamic programming & graph problems", start_time=datetime(2026, 10, 28, 11, 0)),
            EventRound(event_id=14, round_number=3, title="The Boss Round", description="Optimization & bug shootout round", start_time=datetime(2026, 10, 28, 12, 15))
        ])

        # Prizes for Code Sprint
        db.add_all([
            EventPrize(event_id=14, position=1, title="Winner 🥇", amount=25000.00, description="Cash prize + Winner Trophy + Internship Opportunity"),
            EventPrize(event_id=14, position=2, title="First Runner Up 🥈", amount=15000.00, description="Cash prize + Runner-up Trophy"),
            EventPrize(event_id=14, position=3, title="Second Runner Up 🥉", amount=8000.00, description="Cash prize + Certificate of Excellence")
        ])

        # FAQs for Code Sprint
        db.add_all([
            EventFAQ(event_id=14, question="Can I bring my own laptop?", answer="Yes, participants are encouraged to bring their laptops with their preferred IDE installed. Backup desktop terminals will also be provided."),
            EventFAQ(event_id=14, question="Is food provided?", answer="Yes, lunch refreshments and snacks will be provided to all participants.")
        ])

        # Schedules
        db.add_all([
            ScheduleItem(event_id=14, venue_id=v_lab2.id, title="Code Sprint - Algorithms Showdown", description="Intense speed coding challenge", day_number=1, date=date(2026, 10, 28), start_time=time(10, 0), end_time=time(13, 0), category="Technical"),
            ScheduleItem(event_id=19, venue_id=v_lab2.id, title="ByteHack 2026 Kickoff", description="24-hour hackathon opening ceremony", day_number=1, date=date(2026, 10, 28), start_time=time(14, 0), end_time=time(15, 30), category="Technical"),
            ScheduleItem(event_id=18, venue_id=v_seminar.id, title="AI Challenge - Agentic Workshop & Build", description="Multi-modal AI agent development", day_number=2, date=date(2026, 10, 29), start_time=time(9, 30), end_time=time(17, 30), category="Technical"),
            ScheduleItem(event_id=20, venue_id=v_ground.id, title="Battle of the Bands - Grand Finale", description="Top collegiate rock bands live performance", day_number=3, date=date(2026, 10, 30), start_time=time(18, 0), end_time=time(22, 30), category="Cultural"),
        ])
        db.commit()

        # -------------------------------------------------------------
        # 5. TEAMS (ByteHack 2026)
        # -------------------------------------------------------------
        print("  Creating competing teams...")
        t_byteforce = Team(id=45, name="BYTEFORCE", event_id=19, leader_id=joyal_user.id, code="BYTE-9420", is_finalized=True)
        t_codex = Team(id=46, name="CODEX", event_id=19, leader_id=student2.id, code="CDX-9180", is_finalized=True)
        t_debuggers = Team(id=47, name="DEBUGGERS", event_id=19, leader_id=student3.id, code="DBG-8970", is_finalized=True)
        db.add_all([t_byteforce, t_codex, t_debuggers])
        db.commit()

        # Add team members
        db.add_all([
            TeamMember(team_id=t_byteforce.id, user_id=joyal_user.id),
            TeamMember(team_id=t_codex.id, user_id=student2.id),
            TeamMember(team_id=t_debuggers.id, user_id=student3.id),
        ])
        db.commit()

        # -------------------------------------------------------------
        # 6. JUDGE ASSIGNMENT & EVALUATIONS (Matches Prompt Leaderboard)
        # 🥇 BYTEFORCE       94.2
        # 🥈 CODEX           91.8
        # 🥉 DEBUGGERS       89.7
        # -------------------------------------------------------------
        print("  Creating judging evaluations and leaderboard...")
        db.add(JudgeAssignment(event_id=19, judge_id=judge_user.id))
        db.commit()

        # Evaluations
        db.add_all([
            Evaluation(
                event_id=19,
                team_id=t_byteforce.id,
                judge_id=judge_user.id,
                innovation=32.2,
                technical_execution=31.0,
                presentation=31.0,
                total_score=94.2,
                remarks="Outstanding architecture, clean API contract and high scalability."
            ),
            Evaluation(
                event_id=19,
                team_id=t_codex.id,
                judge_id=judge_user.id,
                innovation=31.0,
                technical_execution=30.8,
                presentation=30.0,
                total_score=91.8,
                remarks="Very good implementation and intuitive frontend UI."
            ),
            Evaluation(
                event_id=19,
                team_id=t_debuggers.id,
                judge_id=judge_user.id,
                innovation=30.0,
                technical_execution=29.7,
                presentation=30.0,
                total_score=89.7,
                remarks="Solid concept with good algorithmic efficiency."
            ),
        ])
        db.commit()

        # Leaderboard Results
        db.add_all([
            EventResult(event_id=19, team_id=t_byteforce.id, rank=1, average_score=94.2, total_evaluations=1, is_published=True),
            EventResult(event_id=19, team_id=t_codex.id, rank=2, average_score=91.8, total_evaluations=1, is_published=True),
            EventResult(event_id=19, team_id=t_debuggers.id, rank=3, average_score=89.7, total_evaluations=1, is_published=True),
        ])
        db.commit()

        # -------------------------------------------------------------
        # 7. REGISTRATIONS, PAYMENTS & FEST PASS FOR JOYAL
        # -------------------------------------------------------------
        print("  Creating registrations and verified pass for Joyal (ID 9281)...")
        # Joyal registered for Code Sprint (ID 9281 matching prompt)
        reg_joyal_codesprint = Registration(
            id=9281,  # Matches user specification prompt
            user_id=joyal_user.id,
            event_id=14,
            status=RegistrationStatus.CONFIRMED,
            amount=150.00
        )
        # Joyal registered for ByteHack
        reg_joyal_hack = Registration(
            id=9282,
            user_id=joyal_user.id,
            event_id=19,
            team_id=t_byteforce.id,
            status=RegistrationStatus.CONFIRMED,
            amount=300.00
        )
        db.add_all([reg_joyal_codesprint, reg_joyal_hack])
        db.commit()

        # Payment for Joyal
        pay_codesprint = Payment(
            registration_id=9281,
            user_id=joyal_user.id,
            amount=150.00,
            transaction_id="TXN-9281-CS-789",
            payment_method="UPI",
            status=PaymentStatus.SUCCESS,
            paid_at=datetime(2026, 10, 20, 14, 25)
        )
        db.add(pay_codesprint)
        db.flush()

        inv_codesprint = Invoice(
            payment_id=pay_codesprint.id,
            invoice_number="INV-2026-9281-FST",
            invoice_url="/api/payments/invoice/INV-2026-9281-FST"
        )
        db.add(inv_codesprint)

        # Fest Pass with QR code
        qr_token_joyal = "FEST-PASS-9281-JOYAL-VERIFIED"
        qr_img_path = generate_qr_code_image(qr_token_joyal)

        pass_codesprint = FestPass(
            registration_id=9281,
            qr_token=qr_token_joyal,
            qr_image_url=qr_img_path,
            status=PassStatus.ACTIVE
        )
        db.add(pass_codesprint)

        # Attendance check-in simulation (97 checked in)
        db.add(
            Attendance(
                registration_id=9281,
                event_id=14,
                scanned_by_id=coordinator_user.id,
                status=AttendanceStatus.CHECKED_IN,
                check_in_time=datetime(2026, 10, 28, 9, 42, 18)
            )
        )

        # Certificate for Joyal
        cert_joyal = Certificate(
            certificate_id="FEST-2026-CS-9281",
            registration_id=9281,
            user_id=joyal_user.id,
            event_id=14,
            title="Certificate of Participation",
            pdf_url="/api/certificates/FEST-2026-CS-9281/download",
            is_verified=True
        )
        db.add(cert_joyal)

        # Notifications for Joyal
        db.add_all([
            Notification(
                user_id=joyal_user.id,
                title="Registration Confirmed: Code Sprint",
                message="Your registration is confirmed. Your Fest Pass QR is ready for check-in!",
                type="REGISTRATION",
                link="/passes/9281"
            ),
            Notification(
                user_id=joyal_user.id,
                title="Certificate Issued! 🎓",
                message="Your Certificate of Participation for Code Sprint has been issued. Click to view and download.",
                type="CERTIFICATE",
                link="/certificates"
            ),
        ])
        db.commit()

        # -------------------------------------------------------------
        # 8. SPONSORS & PLANS
        # -------------------------------------------------------------
        print("  Creating sponsors and sponsorship tiers...")
        plan_title = SponsorshipPlan(tier="Title", price=250000.00, perks='["Main stage branding", "Keynote address", "All banners logo", "10 VIP Fest passes", "Recruitment booth"]')
        plan_platinum = SponsorshipPlan(tier="Platinum", price=150000.00, perks='["Event stage branding", "Website header banner", "Social media promotions", "5 VIP passes"]')
        plan_gold = SponsorshipPlan(tier="Gold", price=75000.00, perks='["Event co-branding", "Website listing", "Promotion in event swag bags"]')
        db.add_all([plan_title, plan_platinum, plan_gold])
        db.commit()

        sp_google = Sponsor(
            name="Google Cloud",
            company_name="Google LLC",
            logo_url="https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg",
            website_url="https://cloud.google.com",
            tier="Title",
            reach_count=12400,
            clicks_count=840,
            is_active=True
        )
        sp_intel = Sponsor(
            name="Intel OneAPI",
            company_name="Intel Corporation",
            logo_url="https://upload.wikimedia.org/wikipedia/commons/7/7d/Intel_logo_%282020%29.svg",
            website_url="https://intel.com",
            tier="Platinum",
            reach_count=8200,
            clicks_count=520,
            is_active=True
        )
        sp_redbull = Sponsor(
            name="Red Bull",
            company_name="Red Bull Energy",
            logo_url="https://upload.wikimedia.org/wikipedia/en/f/f5/RedBullEnergyDrink.svg",
            website_url="https://redbull.com",
            tier="Gold",
            reach_count=6500,
            clicks_count=390,
            is_active=True
        )
        db.add_all([sp_google, sp_intel, sp_redbull])
        db.commit()

        print("✅ FESTORA database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during database seeding: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
