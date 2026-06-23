"""Integration and IntegrationCredential models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, LargeBinary, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TEXT
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import CreatedAtMixin, TimestampMixin, uuid_pk


class Integration(TimestampMixin, Base):
    __tablename__ = "integrations"

    id: Mapped[uuid.UUID] = uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(
        nullable=False, default="connected", server_default="connected"
    )
    config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    connected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class IntegrationCredential(CreatedAtMixin, Base):
    __tablename__ = "integration_credentials"
    __table_args__ = (
        UniqueConstraint("integration_id", name="uq_integration_credential_integration"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    integration_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False
    )
    auth_type: Mapped[str] = mapped_column(
        nullable=False, default="oauth2", server_default="oauth2"
    )
    secret_ciphertext: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    key_id: Mapped[str | None] = mapped_column(nullable=True)
    access_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scopes: Mapped[list[str] | None] = mapped_column(ARRAY(TEXT), nullable=True)
