import os
import sys
from pathlib import Path

# Add project root, backend folder, and fest_agents to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
FEST_AGENTS_DIR = BASE_DIR / "fest_agents"

for p in [str(BACKEND_DIR), str(BASE_DIR), str(FEST_AGENTS_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Production Supabase fallback if DATABASE_URL is not set or still pointing to localhost
SUPABASE_URL = "postgresql+psycopg://postgres.blxgujyshjlegkrdpxrn:%29jtu%28dhV_31@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres"

current_db = os.getenv("DATABASE_URL", "").strip()
if not current_db or "localhost" in current_db or "127.0.0.1" in current_db:
    os.environ["DATABASE_URL"] = SUPABASE_URL

# Signal serverless mode for database connection pooling (NullPool)
os.environ["VERCEL"] = "1"

from app.main import app

# Export app for Vercel Serverless Function
