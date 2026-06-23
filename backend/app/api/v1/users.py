"""User profile and membership endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentPrincipal, get_current_principal, paginate
from app.db import get_db
from app.models.tenant import Tenant
from app.models.user import Membership
from app.schemas.auth import MembershipItem, UserProfile, UserProfileUpdate
from app.schemas.common import Page

router = APIRouter()


@router.get("/me/profile", response_model=UserProfile)
def get_profile(principal: CurrentPrincipal = Depends(get_current_principal)) -> UserProfile:
    return UserProfile.model_validate(principal.user)


@router.patch("/me/profile", response_model=UserProfile)
def update_profile(
    body: UserProfileUpdate,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: Session = Depends(get_db),
) -> UserProfile:
    user = principal.user
    for field, value in body.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(user, field, value)
    db.add(user)
    db.flush()
    return UserProfile.model_validate(user)


@router.get("/me/memberships", response_model=Page[MembershipItem])
def list_memberships(
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
) -> Page[MembershipItem]:
    limit, offset = paginate(limit, offset)
    rows = db.execute(
        select(Membership, Tenant)
        .join(Tenant, Tenant.id == Membership.tenant_id)
        .where(Membership.user_id == principal.user.id)
    ).all()
    items = [
        MembershipItem(
            tenant_id=m.tenant_id,
            tenant_name=t.name,
            role=m.role,
            joined_at=m.created_at,
        )
        for m, t in rows
    ]
    total = len(items)
    return Page[MembershipItem](
        items=items[offset : offset + limit], total=total, limit=limit, offset=offset
    )
