import sys
import os
sys.path.extend(['.', 'backend'])

from sqlalchemy import create_engine, text, Boolean
import app.models as models
from app.db.base import Base

mysql_url = 'mysql+pymysql://root:root%40123@localhost:3306/college_fest'
supabase_url = 'postgresql+psycopg://postgres.blxgujyshjlegkrdpxrn:%29jtu%28dhV_31@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres'

print("Connecting to MySQL and Supabase...")
mysql_engine = create_engine(mysql_url)
supa_engine = create_engine(supabase_url)

# Find all boolean columns per table from Base.metadata
bool_cols = {}
for table_name, table in Base.metadata.tables.items():
    bool_cols[table_name] = {col.name for col in table.columns if isinstance(col.type, Boolean)}

tables_in_order = [
    "users",
    "event_categories",
    "venues",
    "events",
    "event_rounds",
    "teams",
    "team_members",
    "registrations",
    "score_criteria",
    "judge_assignments",
    "scores",
    "results",
    "attendance",
    "payments",
    "invoices",
    "certificates",
    "notifications",
    "announcements",
    "sponsorship_plans",
    "sponsorships",
    "promotion_slots",
    "coordinator_applications",
    "judge_applications",
    "sponsor_applications",
    "invitations",
    "audit_logs"
]

with mysql_engine.connect() as mysql_conn, supa_engine.connect() as supa_conn:
    # Disable foreign key constraints during insertion
    supa_conn.execute(text("SET session_replication_role = 'replica';"))
    supa_conn.commit()

    for tbl in tables_in_order:
        try:
            check = mysql_conn.execute(text(f"SHOW TABLES LIKE '{tbl}'")).fetchall()
            if not check:
                continue

            rows = mysql_conn.execute(text(f"SELECT * FROM {tbl}")).mappings().all()
            if not rows:
                print(f"Table '{tbl}': 0 rows")
                continue

            print(f"Migrating '{tbl}': {len(rows)} rows...")
            b_cols = bool_cols.get(tbl, set())
            
            row_dicts = []
            for r in rows:
                d = dict(r)
                # Cast boolean columns
                for c in b_cols:
                    if c in d and d[c] is not None:
                        d[c] = bool(d[c])
                row_dicts.append(d)

            supa_conn.execute(text(f'TRUNCATE TABLE "{tbl}" CASCADE;'))
            supa_conn.commit()

            cols = list(row_dicts[0].keys())
            cols_str = ", ".join([f'"{c}"' for c in cols])
            placeholders = ", ".join([f":{c}" for c in cols])
            insert_sql = text(f'INSERT INTO "{tbl}" ({cols_str}) VALUES ({placeholders})')

            supa_conn.execute(insert_sql, row_dicts)
            supa_conn.commit()
            print(f"  Success: '{tbl}' copied!")

            if "id" in cols:
                try:
                    supa_conn.execute(text(f"SELECT setval(pg_get_serial_sequence('{tbl}', 'id'), COALESCE(max(id), 1)) FROM \"{tbl}\";"))
                    supa_conn.commit()
                except Exception:
                    pass
        except Exception as err:
            supa_conn.rollback()
            print(f"  Error migrating '{tbl}': {err}")

    # Re-enable foreign key constraints
    supa_conn.execute(text("SET session_replication_role = 'origin';"))
    supa_conn.commit()

print("All MySQL records migrated to Supabase successfully!")
