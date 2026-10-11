import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
}

is_sqlite = settings.DATABASE_URL.startswith("sqlite")
is_mysql = "mysql" in settings.DATABASE_URL

if is_sqlite:
    connect_args["check_same_thread"] = False
else:
    # Production connection pooling for MySQL / PostgreSQL
    engine_kwargs["pool_recycle"] = int(os.getenv("DB_POOL_RECYCLE", "1800"))
    engine_kwargs["pool_size"] = int(os.getenv("DB_POOL_SIZE", "10"))
    engine_kwargs["max_overflow"] = int(os.getenv("DB_MAX_OVERFLOW", "20"))

    # Support SSL/TLS for hosted MySQL providers (e.g. Aiven, TiDB Cloud, Railway, AWS RDS)
    db_ssl = os.getenv("DB_SSL", "").lower() in ("true", "1", "required")
    if db_ssl and is_mysql:
        ssl_ca = os.getenv("DB_SSL_CA")
        if ssl_ca and os.path.exists(ssl_ca):
            connect_args["ssl"] = {"ca": ssl_ca}
        else:
            connect_args["ssl"] = {"ssl_mode": "REQUIRED"}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

