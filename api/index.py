import os
import sys
import traceback
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

os.environ["VERCEL"] = "1"

try:
    from app.main import app
except Exception as exc:
    error_trace = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    def debug_error(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Failed to initialize application on Vercel",
                "exception": str(exc),
                "traceback": error_trace.splitlines(),
                "sys_path": sys.path,
                "cwd": os.getcwd(),
                "files_in_cwd": os.listdir(os.getcwd()) if os.path.exists(os.getcwd()) else []
            }
        )
