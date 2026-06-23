"""Auth endpoints: register, login, refresh, me."""

from __future__ import annotations

from datetime import UTC, datetime

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentPrincipal, get_current_principal
from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db import get_db
from app.models.tenant import Tenant
from app.models.user import Membership, User
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    MeResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TenantPublic,
    TokenResponse,
    UserPublic,
)

router = APIRouter()


def _expires_in() -> int:
    return settings.jwt_expire_minutes * 60


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    existing = db.execute(
        select(User).where(func.lower(User.email) == body.email.lower())
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=body.email.lower(),
        full_name=body.full_name,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.flush()

    tenant = Tenant(name=body.tenant_name or (body.full_name or body.email) + "'s workspace")
    db.add(tenant)
    db.flush()

    membership = Membership(tenant_id=tenant.id, user_id=user.id, role="owner")
    db.add(membership)
    db.flush()

    access = create_access_token(str(user.id), tenant_id=str(tenant.id))
    refresh = create_refresh_token(str(user.id), tenant_id=str(tenant.id))

    return RegisterResponse(
        user=UserPublic.model_validate(user),
        tenant=TenantPublic(id=tenant.id, name=tenant.name, role="owner"),
        access_token=access,
        refresh_token=refresh,
        expires_in=_expires_in(),
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.execute(
        select(User).where(func.lower(User.email) == body.email.lower())
    ).scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash or ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    membership = db.execute(
        select(Membership).where(Membership.user_id == user.id)
    ).scalars().first()
    tenant_id = str(membership.tenant_id) if membership else None

    user.last_login_at = datetime.now(UTC)
    db.flush()

    return TokenResponse(
        access_token=create_access_token(str(user.id), tenant_id=tenant_id),
        refresh_token=create_refresh_token(str(user.id), tenant_id=tenant_id),
        expires_in=_expires_in(),
    )


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(body: RefreshRequest) -> AccessTokenResponse:
    try:
        payload = decode_token(body.refresh_token)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid refresh token: {exc}"
        ) from exc
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a refresh token")

    subject = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed token")

    return AccessTokenResponse(
        access_token=create_access_token(str(subject), tenant_id=tenant_id),
        expires_in=_expires_in(),
    )


@router.get("/me", response_model=MeResponse)
def me(principal: CurrentPrincipal = Depends(get_current_principal)) -> MeResponse:
    return MeResponse(
        id=principal.user.id,
        email=principal.user.email,
        full_name=principal.user.full_name,
        active_tenant_id=principal.tenant_id,
        role=principal.role,
        mfa_enabled=principal.user.mfa_enabled,
    )
