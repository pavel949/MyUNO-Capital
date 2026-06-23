"""Agent catalog and run endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.agents.orchestrator import execute_run
from app.agents.registry import AGENT_REGISTRY, roster_metadata
from app.api.deps import (
    CurrentPrincipal,
    get_business_or_404,
    get_current_principal,
    paginate,
)
from app.db import get_db
from app.models.agent import Agent, AgentRun
from app.models.business import Business
from app.schemas.agent import (
    AgentCatalogItem,
    AgentDetail,
    AgentRunAccepted,
    AgentRunListItem,
    AgentRunRequest,
    AgentRunStatus,
)
from app.schemas.common import Page
from app.services.activity import log_activity

router = APIRouter()


@router.get("/agents", response_model=Page[AgentCatalogItem])
def list_agents(
    _: CurrentPrincipal = Depends(get_current_principal),
    limit: int = 20,
    offset: int = 0,
) -> Page[AgentCatalogItem]:
    limit, offset = paginate(limit, offset)
    meta = roster_metadata()
    items = [
        AgentCatalogItem(
            agent=m["agent"],
            category=m["category"],
            description=m["description"],
            min_tier=m["min_tier"],
        )
        for m in meta
    ]
    return Page[AgentCatalogItem](
        items=items[offset : offset + limit], total=len(items), limit=limit, offset=offset
    )


@router.get("/agents/{agent}", response_model=AgentDetail)
def get_agent(agent: str, _: CurrentPrincipal = Depends(get_current_principal)) -> AgentDetail:
    cls = AGENT_REGISTRY.get(agent)
    if cls is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return AgentDetail(
        agent=cls.name,
        category=cls.category,
        description=cls.description,
        inputs=list(cls.inputs_schema),
        high_risk_actions=list(cls.high_risk_actions),
        required_integrations=list(cls.required_integrations),
        min_tier=cls.min_tier,
    )


def _resolve_agent_row(db: Session, agent_name: str) -> Agent | None:
    cls = AGENT_REGISTRY.get(agent_name)
    if cls is None:
        return None
    row = db.execute(select(Agent).where(Agent.key == cls.key)).scalar_one_or_none()
    if row is None:
        # Self-heal: register the agent into the catalog table on first use.
        row = Agent(
            key=cls.key,
            display_name=cls.name,
            category=cls.category,
            description=cls.description,
            default_model=cls.default_model,
            min_tier=cls.min_tier,
            tool_scopes={"integrations": list(cls.required_integrations)},
        )
        db.add(row)
        db.flush()
    return row


@router.post(
    "/businesses/{business_id}/agents/{agent}/run",
    response_model=AgentRunAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
def trigger_run(
    agent: str,
    body: AgentRunRequest,
    business: Business = Depends(get_business_or_404),
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: Session = Depends(get_db),
) -> AgentRunAccepted:
    agent_row = _resolve_agent_row(db, agent)
    if agent_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    run = AgentRun(
        tenant_id=business.tenant_id,
        business_id=business.id,
        agent_id=agent_row.id,
        goal_id=body.goal_id,
        status="queued",
        objective=body.objective,
        inputs=body.inputs or {},
    )
    db.add(run)
    db.flush()

    log_activity(
        db,
        tenant_id=business.tenant_id,
        business_id=business.id,
        actor_type="human",
        actor_id=str(principal.user.id),
        action="agent_run.triggered",
        target_type="agent_run",
        target_id=str(run.id),
        summary=f"Triggered {agent_row.display_name}: {body.objective[:80]}",
    )

    # Execute synchronously so results are available immediately even without a
    # running Celery worker. The same orchestrator path is used by the worker.
    execute_run(db, run.id)
    db.flush()

    return AgentRunAccepted(
        run_id=run.id,
        business_id=business.id,
        agent=agent_row.display_name,
        status="queued",
        created_at=run.created_at,
    )


def _run_to_status(db: Session, run: AgentRun) -> AgentRunStatus:
    agent_row = db.get(Agent, run.agent_id)
    output = run.output or {}
    return AgentRunStatus(
        run_id=run.id,
        agent=agent_row.display_name if agent_row else "Agent",
        status=run.status,
        progress=run.progress,
        started_at=run.started_at,
        finished_at=run.finished_at,
        pending_task_id=output.get("pending_task_id"),
        output=output,
    )


@router.get(
    "/businesses/{business_id}/agents/runs/{run_id}", response_model=AgentRunStatus
)
def get_run(
    run_id: uuid.UUID,
    business: Business = Depends(get_business_or_404),
    db: Session = Depends(get_db),
) -> AgentRunStatus:
    run = db.get(AgentRun, run_id)
    if run is None or run.business_id != business.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return _run_to_status(db, run)


@router.get(
    "/businesses/{business_id}/agents/runs", response_model=Page[AgentRunListItem]
)
def list_runs(
    business: Business = Depends(get_business_or_404),
    db: Session = Depends(get_db),
    agent: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = 20,
    offset: int = 0,
) -> Page[AgentRunListItem]:
    limit, offset = paginate(limit, offset)
    base = select(AgentRun).where(AgentRun.business_id == business.id)
    if status_filter:
        base = base.where(AgentRun.status == status_filter)
    if agent:
        cls = AGENT_REGISTRY.get(agent)
        if cls is not None:
            agent_row = db.execute(
                select(Agent).where(Agent.key == cls.key)
            ).scalar_one_or_none()
            if agent_row is not None:
                base = base.where(AgentRun.agent_id == agent_row.id)

    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(
        base.order_by(AgentRun.created_at.desc()).limit(limit).offset(offset)
    ).scalars().all()

    agent_names = {a.id: a.display_name for a in db.execute(select(Agent)).scalars().all()}
    items = [
        AgentRunListItem(
            run_id=r.id,
            agent=agent_names.get(r.agent_id, "Agent"),
            status=r.status,
            progress=r.progress,
            created_at=r.created_at,
        )
        for r in rows
    ]
    return Page[AgentRunListItem](items=items, total=total, limit=limit, offset=offset)
