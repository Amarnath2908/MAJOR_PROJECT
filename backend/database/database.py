"""
database/database.py — SQLAlchemy Engine & Session Setup
=========================================================
This module configures the SQLAlchemy database connection for the
entire application.  It exposes three objects used everywhere else:

  engine     → The SQLAlchemy Engine connected to the configured DB.
  SessionLocal → A session factory; each call creates a new session.
  Base         → The declarative base class all ORM models inherit from.

And one FastAPI dependency:

  get_db()   → Yields a DB session per request, always closing it after.

Usage
-----
    # In a model file:
    from database.database import Base

    class User(Base):
        __tablename__ = "users"
        ...

    # In a FastAPI route (via dependency injection):
    from database.database import get_db
    from sqlalchemy.orm import Session

    @router.get("/example")
    def example(db: Session = Depends(get_db)):
        ...
"""

from pathlib import Path
from typing import Generator

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Ensure the database directory exists
# ─────────────────────────────────────────────────────────────────────────────

# Extract the file path from the SQLite URL  (sqlite:///./database/designverse.db)
# and create its parent directory if needed.
if settings.DATABASE_URL.startswith("sqlite"):
    db_path_str = settings.DATABASE_URL.replace("sqlite:///", "")
    db_file = Path(db_path_str)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    logger.debug("SQLite database directory ensured: %s", db_file.parent)


engine_kwargs = {
    "echo": settings.DEBUG,
}

if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(
    settings.DATABASE_URL,
    **engine_kwargs,
)
"""
SQLAlchemy Engine.

The engine manages the underlying DBAPI connection pool.  All sessions
are created from this engine via SessionLocal.
"""


# ─────────────────────────────────────────────────────────────────────────────
# Session Factory
# ─────────────────────────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,   # Transactions must be committed explicitly
    autoflush=False,    # Do not automatically flush pending changes before queries
)
"""
Session factory.

Call ``db = SessionLocal()`` to get a new database session.
Always close the session in a finally block or use the get_db() dependency.
"""


# ─────────────────────────────────────────────────────────────────────────────
# Declarative Base
# ─────────────────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """
    Declarative base class for all SQLAlchemy ORM models.

    Every model in database/models.py inherits from this class.
    SQLAlchemy uses the class hierarchy rooted at Base to discover
    all table definitions when calling Base.metadata.create_all().

    Example
    -------
        from database.database import Base

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
    """
    pass


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI Dependency — Database Session
# ─────────────────────────────────────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy database session.

    The session is automatically closed after the request completes,
    even if an exception is raised.  This ensures connections are
    returned to the pool promptly.

    Yields
    ------
    Session
        An active SQLAlchemy ORM session bound to the configured database.

    Usage (in a route)
    ------------------
        from fastapi import Depends
        from sqlalchemy.orm import Session
        from database.database import get_db

        @router.get("/items")
        def list_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db: Session = SessionLocal()
    try:
        yield db
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        logger.error("Database session error: %s", exc)
        db.rollback()
        raise
    finally:
        db.close()
