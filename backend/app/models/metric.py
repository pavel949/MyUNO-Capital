"""Metric and ExitReadiness models."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, SmallInteger, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import uuid_pk


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[uuid.UUID] = uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    metric_key: Mapped[str] = mapped_column(nullable=False)
    value: Mapped[float] = mapped_column(Numeric, nullable=False)
    unit: Mapped[str | None] = mapped_column(nullable=True)
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str | None] = mapped_column(nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ExitReadiness(Base):
    __tablename__ = "exit_readiness"
    __table_args__ = (UniqueConstraint("business_id", name="uq_exit_readiness_business"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    overall_score: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    financials_score: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    metrics_score: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    documentation_score: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    operational_stability_score: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0
    )
    notes: Mapped[str | None] = mapped_column(nullable=True)
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
