"""ActivityLog model — append-only audit trail."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import CreatedAtMixin, uuid_pk


class ActivityLog(CreatedAtMixin, Base):
    __tablename__ = "activity_log"

    id: Mapped[uuid.UUID] = uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    business_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=True
    )
    actor_type: Mapped[str] = mapped_column(nullable=False)
    # actor_id is a free-form id (user uuid or agent key), stored as text.
    actor_id: Mapped[str | None] = mapped_column(nullable=True)
    action: Mapped[str] = mapped_column(nullable=False)
    target_type: Mapped[str | None] = mapped_column(nullable=True)
    target_id: Mapped[str | None] = mapped_column(nullable=True)
    summary: Mapped[str | None] = mapped_column(nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    trace_id: Mapped[str | None] = mapped_column(nullable=True)
