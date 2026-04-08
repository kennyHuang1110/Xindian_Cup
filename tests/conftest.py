"""Shared pytest fixtures for application tests."""

from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_db
from app.core.database import Base, create_db_engine
from app.core.config import get_settings
from app.main import app
from app.models import AuditLog, Blacklist, EmailVerification, Member, Team


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """Create a test client backed by a temporary SQLite database."""
    tmp_dir = Path(".tmp") / "pytest-db"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    db_path = tmp_dir / f"{uuid4().hex}.db"
    engine = create_db_engine(f"sqlite:///{db_path}")
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if db_path.exists():
        db_path.unlink()


@pytest.fixture()
def admin_headers() -> dict[str, str]:
    """Return headers for admin-protected endpoints."""
    settings = get_settings()
    return {"X-Admin-Token": settings.admin_api_token}
