"""Business, goal, and OKR schemas."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class BusinessCreate(BaseModel):
    name: str
    model_template: str | None = None
    description: str | None = None
    autonomy_profile: str = "ask_first"


class BusinessUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    stage: str | None = None
    autonomy_profile: str | None = None


class BusinessOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    model_template: str | None = None
    description: str | None = None
    stage: str
    autonomy_profile: str
    created_at: datetime


class BusinessListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    model_template: str | None = None
    stage: str
    created_at: datetime


class GoalCreate(BaseModel):
    title: str
    description: str | None = None
    target_date: date | None = None
    metric: str | None = None
    target_value: float | None = None


class GoalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    business_id: uuid.UUID
    title: str
    metric: str | None = None
    target_value: float | None = None
    target_date: date | None = None
    status: str
    created_at: datetime


class OKRGenerateRequest(BaseModel):
    horizon: str = "quarter"


class KeyResult(BaseModel):
    kr: str
    target: float
    current: float = 0


class ObjectiveOut(BaseModel):
    id: uuid.UUID
    objective: str
    key_results: list[KeyResult] = Field(default_factory=list)


class OKRGenerateResponse(BaseModel):
    goal_id: uuid.UUID
    objectives: list[ObjectiveOut]
    generated_by: str = "StrategyAgent"
    generated_at: datetime
