"""
Database Session & Connection Management
----------------------------------------
Configures SQLAlchemy engine, connection pooling, and FastAPI session dependency
supporting PostgreSQL (Production / Docker) and SQLite fallback (Local Development).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

logger = logging.getLogger(__name__)

# Determine database URL from environment / .env file
from dotenv import load_dotenv

env_file = Path(__file__).resolve().parents[2] / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Default to PostgreSQL connection string; fall back to SQLite if PG host unreachable
    pg_url = "postgresql+psycopg2://cse_user:cse_password@localhost:5432/cse_db"
    DATABASE_URL = pg_url
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Configure engine with appropriate dialect arguments
if DATABASE_URL.startswith("postgresql"):
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3},
        )
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Connected successfully to PostgreSQL database: %s", DATABASE_URL.split("@")[-1])
    except Exception as exc:
        logger.warning(
            "PostgreSQL is unreachable (%s). Falling back to local SQLite at data/cse.db.",
            exc,
        )
        data_dir = Path("data")
        data_dir.mkdir(parents=True, exist_ok=True)
        sqlite_path = (data_dir / "cse.db").resolve()
        DATABASE_URL = f"sqlite:///{sqlite_path}"
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
        )
        logger.info("Using SQLite fallback at %s", sqlite_path)
else:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy database session per request
    and guarantees proper closure.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Verifies active connectivity to the configured database engine."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error("Database connection check failed: %s", exc)
        return False
