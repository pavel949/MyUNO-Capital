"""Decision and DecisionOption models (Decision Hub)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import CreatedAtMixin, uuid_pk


class Decision(CreatedAtMixin, Base):
    __tablename__ = "decisions"

    id: Mapped[uuid.UUID] = uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    decision_type: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    context: Mapped[str | None] = mapped_column(nullable=True)
    ai_recommendation: Mapped[str | None] = mapped_column(nullable=True)
    overall_call: Mapped[str | None] = mapped_column(nullable=True)
    # chosen_option_id FK is added in the migration after decision_options exists.
    chosen_option_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), nullable=True
    )
    status: Mapped[str] = mapped_column(nullable=False, default="open", server_default="open")
    decided_by: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DecisionOption(CreatedAtMixin, Base):
    __tablename__ = "decision_options"

    id: Mapped[uuid.UUID] = uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    decision_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False
    )
    option_name: Mapped[str] = mapped_column(nullable=False)
    risk_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    complexity_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    potential_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    time_to_impact: Mapped[str | None] = mapped_column(nullable=True)
    capital_required_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    advisor_scores: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )
    ai_justification: Mapped[str | None] = mapped_column(nullable=True)
    is_recommended: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
