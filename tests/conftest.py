"""Shared pytest fixtures for the static public site."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """Create a basic test client for static page rendering."""
    with TestClient(app) as test_client:
        yield test_client
