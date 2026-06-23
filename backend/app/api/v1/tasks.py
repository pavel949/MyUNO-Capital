"""Task endpoints: list, get, approve, reject."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import (
    CurrentPrincipal,
    get_business_or_404,
    get_current_principal,
    paginate,
)
from app.db import get_db
from app.models.agent import AgentRun, Task
from app.models.business import Business
from app.schemas.common import Page
from app.schemas.task import (
    TaskActionResponse,
    TaskApproveRequest,
    TaskDetail,
    TaskListItem,
    TaskRejectRequest,
)
from app.services.activity import log_activity

router = APIRouter()


def _business_run_ids(db: Session, business_id: uuid.UUID) -> list[uuid.UUID]:
    return list(
        db.execute(
            select(AgentRun.id).where(AgentRun.business_id == business_id)
        ).scalars().all()
    )


def _load_task(db: Session, business: Business, task_id: uuid.UUID) -> Task:
    task = db.get(Task, task_id)
    if task is None or task.tenant_id != business.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    run = db.get(AgentRun, task.agent_run_id)
    if run is None or run.business_id != business.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.get("/{business_id}/tasks", response_model=Page[TaskListItem])
def list_tasks(
    business: Business = Depends(get_business_or_404),
    db: Session = Depends(get_db),
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = 20,
    offset: int = 0,
) -> Page[TaskListItem]:
    limit, offset = paginate(limit, offset)
    run_ids = _business_run_ids(db, business.id)
    if not run_ids:
        return Page[TaskListItem](items=[], total=0, limit=limit, offset=offset)

    base = select(Task).where(Task.agent_run_id.in_(run_ids))
    if status_filter:
        base = base.where(Task.status == status_filter)
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(
        base.order_by(Task.created_at.desc()).limit(limit).offset(offset)
    ).scalars().all()
    items = [
        TaskListItem(
            id=t.id,
            title=t.title,
            agent=t.agent_key,
            status=t.status,
            risk_level=t.risk_level,
            created_at=t.created_at,
        )
        for t in rows
    ]
    return Page[TaskListItem](items=items, total=total, limit=limit, offset=offset)


@router.get("/{business_id}/tasks/{task_id}", response_model=TaskDetail)
def get_task(
    task_id: uuid.UUID,
    business: Business = Depends(get_business_or_404),
    db: Session = Depends(get_db),
) -> TaskDetail:
    task = _load_task(db, business, task_id)
    return TaskDetail(
        id=task.id,
        title=task.title,
        agent=task.agent_key,
        type=task.type,
        status=task.status,
        risk_level=task.risk_level,
        payload=task.payload or {},
        result=task.result,
        created_at=task.created_at,
    )


@router.post("/{business_id}/tasks/{task_id}/approve", response_model=TaskActionResponse)
def approve_task(
    task_id: uuid.UUID,
    body: TaskApproveRequest,
    business: Business = Depends(get_business_or_404),
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: Session = Depends(get_db),
) -> TaskActionResponse:
    task = _load_task(db, business, task_id)
    if task.status not in ("pending_approval", "queued"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Task is not awaiting approval (status={task.status})",
        )
    now = datetime.now(UTC)
    task.status = "approved"
    task.approved_by = principal.user.id
    task.approved_at = now

    # Resume the run: the gated action is now allowed to proceed.
    run = db.get(AgentRun, task.agent_run_id)
    if run is not None and run.status == "awaiting_approval":
        run.status = "succeeded"
        run.progress = 1.0
        run.finished_at = now
    db.flush()

    log_activity(
        db,
        tenant_id=business.tenant_id,
        business_id=business.id,
        actor_type="human",
        actor_id=str(principal.user.id),
        action="task.approved",
        target_type="task",
        target_id=str(task.id),
        summary=f"Approved task. {body.note or ''}".strip(),
    )
    return TaskActionResponse(
        id=task.id, status=task.status, approved_by=task.approved_by, approved_at=task.approved_at
    )


@router.post("/{business_id}/tasks/{task_id}/reject", response_model=TaskActionResponse)
def reject_task(
    task_id: uuid.UUID,
    body: TaskRejectRequest,
    business: Business = Depends(get_business_or_404),
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: Session = Depends(get_db),
) -> TaskActionResponse:
    task = _load_task(db, business, task_id)
    if task.status not in ("pending_approval", "queued"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Task is not awaiting approval (status={task.status})",
        )
    task.status = "rejected"

    run = db.get(AgentRun, task.agent_run_id)
    if run is not None and run.status == "awaiting_approval":
        run.status = "cancelled"
        run.finished_at = datetime.now(UTC)
    db.flush()

    log_activity(
        db,
        tenant_id=business.tenant_id,
        business_id=business.id,
        actor_type="human",
        actor_id=str(principal.user.id),
        action="task.rejected",
        target_type="task",
        target_id=str(task.id),
        summary=f"Rejected task. {body.reason or ''}".strip(),
    )
    return TaskActionResponse(id=task.id, status=task.status)
