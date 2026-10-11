import os
import sys
from pathlib import Path

# Add frontend directory and root to sys.path so app and fest_agents can be imported
FRONTEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = FRONTEND_DIR.parent
for p in [str(FRONTEND_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Production Supabase database connection
SUPABASE_URL = "postgresql+psycopg://postgres.blxgujyshjlegkrdpxrn:%29jtu%28dhV_31@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres"

current_db = os.getenv("DATABASE_URL", "").strip()
if not current_db or "localhost" in current_db or "127.0.0.1" in current_db:
    os.environ["DATABASE_URL"] = SUPABASE_URL

os.environ["VERCEL"] = "1"

from app.main import app

# Export app for Vercel Serverless Function
