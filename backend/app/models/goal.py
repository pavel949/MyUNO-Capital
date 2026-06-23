"""Goal and OKR models."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import CreatedAtMixin, uuid_pk


class Goal(CreatedAtMixin, Base):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    metric: Mapped[str | None] = mapped_column(nullable=True)
    target_value: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, default="active", server_default="active")


class OKR(CreatedAtMixin, Base):
    __tablename__ = "okrs"

    id: Mapped[uuid.UUID] = uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    goal_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False
    )
    objective: Mapped[str] = mapped_column(nullable=False)
    key_result: Mapped[str] = mapped_column(nullable=False)
    target_value: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    current_value: Mapped[float | None] = mapped_column(
        Numeric, nullable=True, default=0, server_default="0"
    )
    unit: Mapped[str | None] = mapped_column(nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        nullable=False, default="on_track", server_default="on_track"
    )
