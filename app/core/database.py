"""Database engine and session configuration."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()


def create_db_engine(database_url: str | None = None) -> Engine:
    """Build an engine for the configured database backend."""
    resolved_url = database_url or settings.database_url
    engine_kwargs: dict[str, object] = {
        "future": True,
        "pool_pre_ping": not resolved_url.startswith("sqlite"),
    }
    if resolved_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(resolved_url, **engine_kwargs)


engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Base declarative class for ORM models."""

    pass
