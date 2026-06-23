"""Pytest fixtures. Configures env so the app imports without a real .env."""

from __future__ import annotations

import os

os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-your-anthropic-api-key-here")  # placeholder -> stub

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)
