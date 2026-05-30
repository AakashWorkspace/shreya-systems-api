import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shreya_local.db")

# Neon/Supabase uses postgres:// but SQLAlchemy needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

_is_pg = "postgresql" in DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"} if _is_pg else {},
    pool_pre_ping=True,
    # Tune pool for Neon serverless (free tier caps at ~5-10 connections).
    # SQLite uses StaticPool internally so these kwargs are ignored for it.
    **(
        {
            "pool_size": 3,       # max persistent connections
            "max_overflow": 2,    # extra connections allowed under load
            "pool_recycle": 300,  # recycle every 5 min (Neon idles at 5 min)
            "pool_timeout": 30,   # fail fast if no connection available
        }
        if _is_pg else {}
    ),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
