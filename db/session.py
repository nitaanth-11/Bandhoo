"""
Database session, connection pooling, and credential-safe health management for Bandhoo.
Supports PostgreSQL (with production connection pooling and resiliency)
as well as local fallback for development/testing environments.
"""

import os
import re
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Environment variable configuration (never hardcode credentials)
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///bandhoo_persistence.db")

# Connection pool configurations
DB_POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.environ.get("DB_MAX_OVERFLOW", "20"))
DB_POOL_TIMEOUT = int(os.environ.get("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.environ.get("DB_POOL_RECYCLE", "1800"))


def mask_db_url(url: str) -> str:
    """
    Masks credentials in database connection URLs for safe logging and error reporting.
    Example: postgresql://user:secret@localhost:5432/db -> postgresql://user:***@localhost:5432/db
    """
    if not url:
        return ""
    return re.sub(r"://([^:@]+):([^@]+)@", r"://\1:***@", url)


def create_configured_engine(url: str = DATABASE_URL):
    """
    Builds a SQLAlchemy engine with safe pooling, pre-ping, and timeout options.
    """
    connect_args = {}
    engine_kwargs = {
        "pool_pre_ping": True,
        "echo": False
    }

    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        engine_kwargs["connect_args"] = connect_args
    else:
        # PostgreSQL / MySQL connection pool controls
        engine_kwargs["pool_size"] = DB_POOL_SIZE
        engine_kwargs["max_overflow"] = DB_MAX_OVERFLOW
        engine_kwargs["pool_timeout"] = DB_POOL_TIMEOUT
        engine_kwargs["pool_recycle"] = DB_POOL_RECYCLE

    return create_engine(url, **engine_kwargs)


engine = create_configured_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for scoped request operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations with auto-rollback."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_db_health() -> dict:
    """
    Verifies database connectivity and executes a health check ping.
    Guarantees no raw passwords or sensitive credentials are returned.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "dialect": engine.name,
            "connected": True,
            "url_sanitized": mask_db_url(str(engine.url))
        }
    except Exception as exc:
        sanitized_error = mask_db_url(str(exc))
        return {
            "status": "unhealthy",
            "dialect": engine.name,
            "connected": False,
            "error": sanitized_error
        }


def init_db(target_engine=None):
    """Initializes schema tables if not existing."""
    from db import models  # noqa: F401
    bind_engine = target_engine or engine
    Base.metadata.create_all(bind=bind_engine)
