"""Decision Hub schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class OptionCreate(BaseModel):
    name: str
    factors: dict[str, Any] = Field(default_factory=dict)


class DecisionCreate(BaseModel):
    title: str
    type: str
    context: str | None = None
    options: list[OptionCreate] = Field(default_factory=list)


class DecisionCreated(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    title: str
    type: str
    status: str
    created_at: datetime


class OptionListItem(BaseModel):
    id: uuid.UUID
    name: str
    risk: int | None = None
    complexity: int | None = None
    potential: int | None = None
    time_to_impact: str | None = None
    capital_required: str | None = None
    ai_recommendation: str | None = None


class OptionDetail(BaseModel):
    id: uuid.UUID
    name: str
    risk: int | None = None
    complexity: int | None = None
    potential: int | None = None
    advisor_scores: dict[str, Any] = Field(default_factory=dict)
    overall_call: str | None = None
    justification: str | None = None
    is_recommended: bool = False


class DecisionDetail(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    type: str
    ai_recommendation: str | None = None
    overall_call: str | None = None
    options: list[OptionDetail] = Field(default_factory=list)


class DecisionSelectRequest(BaseModel):
    option_id: uuid.UUID
    note: str | None = None


class DecisionSelectResponse(BaseModel):
    id: uuid.UUID
    status: str
    selected_option_id: uuid.UUID
    decided_at: datetime
