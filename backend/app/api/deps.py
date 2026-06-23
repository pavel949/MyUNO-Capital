"""FastAPI dependencies: DB session, current user, tenant scoping."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db import get_db
from app.models.business import Business
from app.models.user import Membership, User

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class CurrentPrincipal:
    user: User
    tenant_id: uuid.UUID
    role: str


def _unauthorized(message: str = "Missing or invalid credentials") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
    db: Session = Depends(get_db),
) -> CurrentPrincipal:
    if credentials is None or not credentials.credentials:
        raise _unauthorized()

    try:
        payload = decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise _unauthorized(f"Invalid token: {exc}") from exc

    if payload.get("type") != "access":
        raise _unauthorized("Not an access token")

    user_id = payload.get("sub")
    if not user_id:
        raise _unauthorized("Token missing subject")

    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError as exc:
        raise _unauthorized("Malformed subject") from exc

    user = db.get(User, user_uuid)
    if user is None:
        raise _unauthorized("User not found")

    # Resolve active tenant: X-Tenant-Id header overrides the JWT claim.
    tenant_claim = x_tenant_id or payload.get("tenant_id")
    memberships = db.execute(
        select(Membership).where(Membership.user_id == user_uuid)
    ).scalars().all()
    if not memberships:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User has no tenant memberships"
        )

    membership = None
    if tenant_claim:
        try:
            tenant_uuid = uuid.UUID(str(tenant_claim))
            membership = next((m for m in memberships if m.tenant_id == tenant_uuid), None)
        except ValueError:
            membership = None
    if membership is None:
        membership = memberships[0]

    return CurrentPrincipal(user=user, tenant_id=membership.tenant_id, role=membership.role)


def get_business_or_404(
    business_id: uuid.UUID,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: Session = Depends(get_db),
) -> Business:
    """Load a business scoped to the current tenant (404 if not in tenant)."""
    business = db.get(Business, business_id)
    if (
        business is None
        or business.tenant_id != principal.tenant_id
        or business.deleted_at is not None
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return business


def paginate(limit: int = 20, offset: int = 0) -> tuple[int, int]:
    """Clamp limit/offset to the documented bounds (limit max 100)."""
    limit = max(1, min(100, limit))
    offset = max(0, offset)
    return limit, offset
