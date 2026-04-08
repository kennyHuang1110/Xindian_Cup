"""Shared dependency helpers for API routes."""

from collections.abc import Generator

from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal

settings = get_settings()


def get_db() -> Generator[Session, None, None]:
    """Provide a per-request SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_admin_token(x_admin_token: str | None = Header(default=None)) -> None:
    """Require the configured admin API token for admin endpoints."""
    if x_admin_token != settings.admin_api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid admin token is required.",
        )
