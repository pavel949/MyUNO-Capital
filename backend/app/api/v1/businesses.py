"""Business CRUD endpoints."""

from __future__ import annotations

from datetime import UTC

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import (
    CurrentPrincipal,
    get_business_or_404,
    get_current_principal,
    paginate,
)
from app.db import get_db
from app.models.business import Business
from app.schemas.business import (
    BusinessCreate,
    BusinessListItem,
    BusinessOut,
    BusinessUpdate,
)
from app.schemas.common import Page
from app.services.activity import log_activity

router = APIRouter()


@router.get("", response_model=Page[BusinessListItem])
def list_businesses(
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: Session = Depends(get_db),
    stage: str | None = Query(default=None),
    limit: int = 20,
    offset: int = 0,
) -> Page[BusinessListItem]:
    limit, offset = paginate(limit, offset)
    base = select(Business).where(
        Business.tenant_id == principal.tenant_id, Business.deleted_at.is_(None)
    )
    if stage:
        base = base.where(Business.stage == stage)

    total = db.execute(
        select(func.count()).select_from(base.subquery())
    ).scalar_one()
    rows = db.execute(
        base.order_by(Business.created_at.desc()).limit(limit).offset(offset)
    ).scalars().all()
    return Page[BusinessListItem](
        items=[BusinessListItem.model_validate(b) for b in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=BusinessOut, status_code=status.HTTP_201_CREATED)
def create_business(
    body: BusinessCreate,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: Session = Depends(get_db),
) -> BusinessOut:
    business = Business(
        tenant_id=principal.tenant_id,
        name=body.name,
        model_template=body.model_template,
        description=body.description,
        autonomy_profile=body.autonomy_profile,
    )
    db.add(business)
    db.flush()
    log_activity(
        db,
        tenant_id=principal.tenant_id,
        business_id=business.id,
        actor_type="human",
        actor_id=str(principal.user.id),
        action="business.created",
        target_type="business",
        target_id=str(business.id),
        summary=f"Created business '{business.name}'.",
    )
    return BusinessOut.model_validate(business)


@router.get("/{business_id}", response_model=BusinessOut)
def get_business(business: Business = Depends(get_business_or_404)) -> BusinessOut:
    return BusinessOut.model_validate(business)


@router.patch("/{business_id}", response_model=BusinessOut)
def update_business(
    body: BusinessUpdate,
    business: Business = Depends(get_business_or_404),
    db: Session = Depends(get_db),
) -> BusinessOut:
    for field, value in body.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(business, field, value)
    db.add(business)
    db.flush()
    return BusinessOut.model_validate(business)


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business(
    business: Business = Depends(get_business_or_404),
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: Session = Depends(get_db),
) -> Response:
    from datetime import datetime

    business.deleted_at = datetime.now(UTC)
    db.add(business)
    log_activity(
        db,
        tenant_id=principal.tenant_id,
        business_id=business.id,
        actor_type="human",
        actor_id=str(principal.user.id),
        action="business.deleted",
        target_type="business",
        target_id=str(business.id),
        summary=f"Soft-deleted business '{business.name}'.",
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
