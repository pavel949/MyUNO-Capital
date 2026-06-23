"""Task schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TaskListItem(BaseModel):
    id: uuid.UUID
    title: str | None = None
    agent: str | None = None
    status: str
    risk_level: str
    created_at: datetime


class TaskDetail(BaseModel):
    id: uuid.UUID
    title: str | None = None
    agent: str | None = None
    type: str
    status: str
    risk_level: str
    payload: dict[str, Any]
    result: dict[str, Any] | None = None
    created_at: datetime


class TaskApproveRequest(BaseModel):
    note: str | None = None


class TaskRejectRequest(BaseModel):
    reason: str | None = None


class TaskActionResponse(BaseModel):
    id: uuid.UUID
    status: str
    approved_by: uuid.UUID | None = None
    approved_at: datetime | None = None
