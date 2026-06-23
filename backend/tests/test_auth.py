"""Auth tests. Security primitives run offline; HTTP register/login may skip
without a reachable database."""

from __future__ import annotations

import uuid

import jwt
import pytest

from app.config import settings
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db import engine


def test_password_hash_roundtrip() -> None:
    h = hash_password("S3cure-passphrase!")
    assert h != "S3cure-passphrase!"
    assert verify_password("S3cure-passphrase!", h)
    assert not verify_password("wrong", h)


def test_access_token_roundtrip() -> None:
    uid = str(uuid.uuid4())
    tid = str(uuid.uuid4())
    token = create_access_token(uid, tenant_id=tid)
    payload = decode_token(token)
    assert payload["sub"] == uid
    assert payload["tenant_id"] == tid
    assert payload["type"] == "access"


def test_decode_rejects_tampered_token() -> None:
    token = create_access_token(str(uuid.uuid4()))
    with pytest.raises(jwt.PyJWTError):
        jwt.decode(token + "x", settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def _db_available() -> bool:
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_available(), reason="database not reachable")
def test_register_and_login_flow(client) -> None:
    email = f"test-{uuid.uuid4().hex[:8]}@myuno.dev"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "S3cure-passphrase!",
            "full_name": "Test User",
            "tenant_name": "Test Co",
        },
    )
    assert reg.status_code == 201, reg.text
    data = reg.json()
    assert data["tenant"]["role"] == "owner"
    access = data["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200
    assert me.json()["email"] == email

    login = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "S3cure-passphrase!"}
    )
    assert login.status_code == 200
    assert "access_token" in login.json()
