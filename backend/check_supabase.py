from app.core.config import settings
from sqlalchemy import create_engine, text

engine = create_engine(settings.DATABASE_URL)

try:
    with engine.connect() as connection:
        print("Connected database:", connection.execute(text("SELECT current_database()")).scalar())
        print("Public table count:", connection.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'")).scalar())
finally:
    engine.dispose()
