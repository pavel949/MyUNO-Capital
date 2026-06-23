"""Agent catalog and run schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentCatalogItem(BaseModel):
    agent: str
    category: str
    description: str
    min_tier: str


class AgentDetail(BaseModel):
    agent: str
    category: str
    description: str
    inputs: list[str] = Field(default_factory=list)
    high_risk_actions: list[str] = Field(default_factory=list)
    required_integrations: list[str] = Field(default_factory=list)
    min_tier: str


class AgentRunRequest(BaseModel):
    objective: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    goal_id: uuid.UUID | None = None


class AgentRunAccepted(BaseModel):
    run_id: uuid.UUID
    business_id: uuid.UUID
    agent: str
    status: str
    created_at: datetime


class AgentRunStatus(BaseModel):
    run_id: uuid.UUID
    agent: str
    status: str
    progress: float
    started_at: datetime | None = None
    finished_at: datetime | None = None
    pending_task_id: str | None = None
    output: dict[str, Any] | None = None


class AgentRunListItem(BaseModel):
    run_id: uuid.UUID
    agent: str
    status: str
    progress: float
    created_at: datetime
