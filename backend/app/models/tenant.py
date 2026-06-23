"""Tenant model — top-level account for a solo founder / studio."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, uuid_pk


class Tenant(TimestampMixin, Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(nullable=False)
    plan_tier: Mapped[str] = mapped_column(nullable=False, default="free", server_default="free")
    task_quota_month: Mapped[int] = mapped_column(nullable=False, default=50, server_default="50")
    status: Mapped[str] = mapped_column(nullable=False, default="active", server_default="active")
