"""Activity log endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_business_or_404, paginate
from app.db import get_db
from app.models.activity import ActivityLog
from app.models.business import Business
from app.schemas.common import Page
from app.schemas.metric import ActivityItem

router = APIRouter()


def _target(entry: ActivityLog) -> str | None:
    if entry.target_type and entry.target_id:
        return f"{entry.target_type}:{entry.target_id}"
    return None


@router.get("/{business_id}/activity", response_model=Page[ActivityItem])
def list_activity(
    business: Business = Depends(get_business_or_404),
    db: Session = Depends(get_db),
    actor_type: str | None = Query(default=None),
    agent: str | None = Query(default=None),
    since: datetime | None = Query(default=None),
    limit: int = 20,
    offset: int = 0,
) -> Page[ActivityItem]:
    limit, offset = paginate(limit, offset)
    base = select(ActivityLog).where(ActivityLog.business_id == business.id)
    if actor_type:
        base = base.where(ActivityLog.actor_type == actor_type)
    if agent:
        base = base.where(ActivityLog.actor_id == agent)
    if since:
        base = base.where(ActivityLog.created_at >= since)

    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(
        base.order_by(ActivityLog.created_at.desc()).limit(limit).offset(offset)
    ).scalars().all()
    items = [
        ActivityItem(
            id=e.id,
            actor_type=e.actor_type,
            actor_id=e.actor_id,
            action=e.action,
            target=_target(e),
            summary=e.summary,
            created_at=e.created_at,
        )
        for e in rows
    ]
    return Page[ActivityItem](items=items, total=total, limit=limit, offset=offset)
