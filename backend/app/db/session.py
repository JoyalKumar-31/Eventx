import os
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Normalize database URL: ensure mysql:// uses pymysql driver
database_url = settings.DATABASE_URL
if database_url.startswith("mysql://"):
    database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)

connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
}

is_sqlite = database_url.startswith("sqlite")
is_mysql = "mysql" in database_url

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
    database_url,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

