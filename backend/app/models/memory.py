"""MemoryEntry model — pgvector semantic memory."""

from __future__ import annotations

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import CreatedAtMixin, uuid_pk

EMBEDDING_DIM = 1536


class MemoryEntry(CreatedAtMixin, Base):
    __tablename__ = "memory_entries"

    id: Mapped[uuid.UUID] = uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    scope: Mapped[str] = mapped_column(nullable=False, default="company", server_default="company")
    source_type: Mapped[str | None] = mapped_column(nullable=True)
    source_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)
    content: Mapped[str] = mapped_column(nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
