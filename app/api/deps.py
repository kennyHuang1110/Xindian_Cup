"""Shared dependency helpers for API routes."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Provide a per-request SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
