import sys
import os

# Set paths
sys.path.extend(['.', 'backend'])

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import app.models as models

mysql_url = 'mysql+pymysql://root:root%40123@localhost:3306/college_fest'
supabase_url = 'postgresql+psycopg://postgres.blxgujyshjlegkrdpxrn:%29jtu%28dhV_31@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres'

print("Connecting to databases...")
mysql_engine = create_engine(mysql_url)
supabase_engine = create_engine(supabase_url)

MySQLSession = sessionmaker(bind=mysql_engine)
SupabaseSession = sessionmaker(bind=supabase_engine)

mysql_db = MySQLSession()
supa_db = SupabaseSession()

tables_in_order = [
    (models.user.User, "users"),
    (models.event.EventCategory, "event_categories"),
    (models.event.Venue, "venues"),
    (models.event.Event, "events"),
    (models.event.EventRound, "event_rounds"),
    (models.registration.Team, "teams"),
    (models.registration.TeamMember, "team_members"),
    (models.registration.Registration, "registrations"),
    (models.judging.ScoreCriteria, "score_criteria"),
    (models.judging.JudgeAssignment, "judge_assignments"),
    (models.judging.Score, "scores"),
    (models.judging.Result, "results"),
    (models.attendance.Attendance, "attendance"),
    (models.payment.Payment, "payments"),
    (models.payment.Invoice, "invoices"),
    (models.certificate.Certificate, "certificates"),
    (models.notification.Notification, "notifications"),
    (models.announcement.Announcement, "announcements"),
    (models.sponsor.SponsorshipPlan, "sponsorship_plans"),
    (models.sponsor.Sponsorship, "sponsorships"),
    (models.sponsor.PromotionSlot, "promotion_slots"),
    (models.application.CoordinatorApplication, "coordinator_applications"),
    (models.application.JudgeApplication, "judge_applications"),
    (models.application.SponsorApplication, "sponsor_applications"),
    (models.application.Invitation, "invitations"),
    (models.audit_log.AuditLog, "audit_logs")
]

try:
    for item in tables_in_order:
        model_cls, table_name = item
        try:
            records = mysql_db.query(model_cls).all()
            if not records:
                continue
            
            print(f"Migrating {len(records)} records from {table_name}...")
            
            for r in records:
                # Merge into Supabase
                supa_db.merge(r)
            
            supa_db.commit()
            print(f"  ✓ {table_name} successfully migrated!")
        except Exception as e:
            supa_db.rollback()
            print(f"  ⚠ Error migrating {table_name}: {e}")
            
    # Reset Postgres ID sequences
    print("Updating postgres auto-increment sequences...")
    for item in tables_in_order:
        _, table_name = item
        try:
            supa_db.execute(text(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), COALESCE(max(id), 1)) FROM {table_name};"))
            supa_db.commit()
        except Exception:
            supa_db.rollback()
            pass
            
    print("--- Migration from MySQL to Supabase complete! ---")
finally:
    mysql_db.close()
    supa_db.close()
