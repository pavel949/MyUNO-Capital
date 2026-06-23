"""Agent registry, AgentRun, and Task models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import CreatedAtMixin, TimestampMixin, uuid_pk


class Agent(TimestampMixin, Base):
    """Global/system-seeded catalog of agent types (not tenant-scoped)."""

    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = uuid_pk()
    key: Mapped[str] = mapped_column(unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    default_model: Mapped[str] = mapped_column(
        nullable=False, default="claude-sonnet-4-6", server_default="claude-sonnet-4-6"
    )
    min_tier: Mapped[str] = mapped_column(nullable=False, default="free", server_default="free")
    tool_scopes: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )


class AgentRun(CreatedAtMixin, Base):
    __tablename__ = "agent_runs"

    id: Mapped[uuid.UUID] = uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("agents.id"), nullable=False
    )
    goal_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        nullable=False, default="planned", server_default="planned"
    )
    objective: Mapped[str | None] = mapped_column(nullable=True)
    inputs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    progress: Mapped[float] = mapped_column(nullable=False, default=0.0, server_default="0")
    model_used: Mapped[str | None] = mapped_column(nullable=True)
    token_input: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    token_output: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Task(CreatedAtMixin, Base):
    __tablename__ = "tasks"
    __table_args__ = (
        UniqueConstraint("tenant_id", "idempotency_key", name="uq_task_tenant_idempotency"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    agent_run_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False
    )
    parent_task_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str | None] = mapped_column(nullable=True)
    type: Mapped[str] = mapped_column(nullable=False)
    agent_key: Mapped[str | None] = mapped_column(nullable=True)
    risk_level: Mapped[str] = mapped_column(nullable=False, default="low", server_default="low")
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, default="queued", server_default="queued")
    idempotency_key: Mapped[str] = mapped_column(nullable=False)
    attempts: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0"
    )
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
