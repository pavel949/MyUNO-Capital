"""Helper to write activity_log entries."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.activity import ActivityLog


def log_activity(
    db: Session,
    *,
    tenant_id: uuid.UUID,
    action: str,
    actor_type: str = "system",
    actor_id: str | None = None,
    business_id: uuid.UUID | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    summary: str | None = None,
    meta: dict | None = None,
    trace_id: str | None = None,
) -> ActivityLog:
    """Create and flush an ActivityLog row. Caller controls commit."""
    entry = ActivityLog(
        tenant_id=tenant_id,
        business_id=business_id,
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        summary=summary,
        meta=meta or {},
        trace_id=trace_id,
    )
    db.add(entry)
    db.flush()
    return entry
