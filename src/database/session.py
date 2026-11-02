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

def _sanitize_database_url(raw_val: str | None) -> str:
    """
    Sanitizes DATABASE_URL from environment or GitHub Secrets, handling:
      - Leading/trailing whitespace, newlines, or quotes
      - Accidental 'DATABASE_URL=' key prefix or multi-line .env paste
      - 'postgres://' -> 'postgresql+psycopg2://' normalization
    """
    if not raw_val:
        return ""
    cleaned = raw_val.strip()
    # If multi-line content was pasted into a secret, pick the first non-comment URL line
    for line in cleaned.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.upper().startswith("DATABASE_URL"):
            _, _, line = line.partition("=")
            line = line.strip()
        line = line.strip("'").strip('"').strip()
        if line:
            cleaned = line
            break
    if cleaned.startswith("postgres://"):
        cleaned = cleaned.replace("postgres://", "postgresql+psycopg2://", 1)
    elif cleaned.startswith("postgresql://"):
        cleaned = cleaned.replace("postgresql://", "postgresql+psycopg2://", 1)
    return cleaned


def _use_sqlite_fallback():
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    sqlite_path = (data_dir / "cse.db").resolve()
    fallback_url = f"sqlite:///{sqlite_path}"
    fallback_engine = create_engine(
        fallback_url,
        connect_args={"check_same_thread": False},
    )
    logger.info("Using SQLite fallback at %s", sqlite_path)
    return fallback_url, fallback_engine


DATABASE_URL = _sanitize_database_url(os.getenv("DATABASE_URL"))

if not DATABASE_URL:
    DATABASE_URL = "postgresql+psycopg2://cse_user:cse_password@localhost:5432/cse_db"

# Configure engine with full resilience against invalid URLs or unreachable hosts
try:
    if DATABASE_URL.startswith("postgresql"):
        engine = create_engine(
            DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3},
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Connected successfully to PostgreSQL database: %s", DATABASE_URL.split("@")[-1])
    else:
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
except Exception as exc:
    logger.warning(
        "Primary DATABASE_URL unavailable or invalid (%s). Falling back to local SQLite at data/cse.db.",
        exc,
    )
    DATABASE_URL, engine = _use_sqlite_fallback()

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
