"""
Database session and connection management for Bandhoo.
Supports PostgreSQL with fallback for isolated unit test environments.
"""

import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Environment variable configuration (never hardcode credentials)
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///bandhoo_persistence.db")

# Handle SQLite vs PostgreSQL engine arguments
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI or scoped operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
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
    """Verifies database connectivity and executes a health check ping."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": engine.name, "connected": True}
    except Exception as exc:
        return {"status": "unhealthy", "database": engine.name, "connected": False, "error": str(exc)}


def init_db():
    """Initializes schema tables if not existing."""
    from db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
