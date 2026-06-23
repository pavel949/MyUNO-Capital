"""Metrics, exit-readiness, integration, and activity schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class MetricsResponse(BaseModel):
    business_id: uuid.UUID
    period: str
    mrr: float = 0
    mrr_growth_pct: float = 0
    churn_rate_pct: float = 0
    cac: float = 0
    ltv: float = 0
    ltv_cac_ratio: float = 0
    signups: float = 0
    nps: float = 0
    updated_at: datetime


class ExitReadinessComponents(BaseModel):
    financials: int
    metrics: int
    documentation: int
    operational_stability: int


class ExitReadinessResponse(BaseModel):
    business_id: uuid.UUID
    exit_readiness_score: int
    components: ExitReadinessComponents
    recommendation: str
    updated_at: datetime


class IntegrationItem(BaseModel):
    provider: str
    category: str | None = None
    status: str
    connected_at: datetime | None = None


class IntegrationConnectRequest(BaseModel):
    redirect_uri: str


class IntegrationConnectResponse(BaseModel):
    provider: str
    authorization_url: str
    state: str


class ActivityItem(BaseModel):
    id: uuid.UUID
    actor_type: str
    actor_id: str | None = None
    action: str
    target: str | None = None
    summary: str | None = None
    created_at: datetime = Field(...)
