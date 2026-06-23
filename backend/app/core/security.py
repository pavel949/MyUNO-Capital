"""Security primitives: password hashing (bcrypt) and JWT (PyJWT)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.config import settings

# bcrypt has a hard 72-byte limit on the input password.
_BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt; returns a utf-8 hash string."""
    pw = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    if not password_hash:
        return False
    pw = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    try:
        return bcrypt.checkpw(pw, password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(
    subject: str,
    tenant_id: str | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Mint a short-lived access token. `tenant_id` is encoded as a claim."""
    claims: dict[str, Any] = dict(extra_claims or {})
    if tenant_id is not None:
        claims["tenant_id"] = tenant_id
    return _create_token(
        subject,
        "access",
        timedelta(minutes=settings.jwt_expire_minutes),
        claims,
    )


def create_refresh_token(subject: str, tenant_id: str | None = None) -> str:
    """Mint a long-lived refresh token."""
    claims: dict[str, Any] = {}
    if tenant_id is not None:
        claims["tenant_id"] = tenant_id
    return _create_token(
        subject,
        "refresh",
        timedelta(days=settings.jwt_refresh_expire_days),
        claims,
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT. Raises jwt.PyJWTError on failure."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
