"""Health endpoint tests — must pass with no external services."""

from __future__ import annotations


def test_healthz(client) -> None:
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_openapi_available(client) -> None:
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    body = resp.json()
    assert body["info"]["title"] == "MyUNO Capital API"
    # A few representative routes are mounted under /api/v1.
    assert "/api/v1/auth/login" in body["paths"]
    assert "/api/v1/businesses" in body["paths"]


def test_readyz_returns_json(client) -> None:
    # readyz checks the DB; without one it returns 503 but always valid JSON.
    resp = client.get("/readyz")
    assert resp.status_code in (200, 503)
    assert "status" in resp.json()
