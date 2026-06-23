"""Agent Orchestrator — builds context, invokes an agent, persists artifacts.

Used by both the API (synchronous trigger path) and the Celery task. Given an
agent_run row id, it loads the run + business, runs the mapped agent through the
LLM router, persists the result onto the run, optionally creates a pending
approval task, and writes the activity log.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agents.base import AgentContext, AutonomyProfile
from app.agents.registry import get_agent_class
from app.llm.router import get_llm_router
from app.models.agent import Agent, AgentRun, Task
from app.models.business import Business
from app.services.activity import log_activity


def _autonomy(profile: str | None) -> AutonomyProfile:
    mapping = {
        "ask_first": AutonomyProfile.ASK_FIRST,
        "guided": AutonomyProfile.GUIDED,
        "autonomous_within_limits": AutonomyProfile.AUTONOMOUS,
    }
    return mapping.get(profile or "ask_first", AutonomyProfile.ASK_FIRST)


def execute_run(db: Session, run_id: uuid.UUID) -> AgentRun:
    """Execute the agent for a given agent_run and persist results."""
    run = db.get(AgentRun, run_id)
    if run is None:
        raise ValueError(f"AgentRun {run_id} not found")

    agent_row = db.get(Agent, run.agent_id)
    business = db.get(Business, run.business_id)
    if agent_row is None or business is None:
        run.status = "failed"
        run.output = {"error": "missing agent or business"}
        db.flush()
        return run

    agent_cls = get_agent_class(agent_row.display_name) or get_agent_class(agent_row.key)
    if agent_cls is None:
        run.status = "failed"
        run.output = {"error": f"no agent class for {agent_row.display_name}"}
        db.flush()
        return run

    run.status = "running"
    run.started_at = datetime.now(UTC)
    db.flush()

    ctx = AgentContext(
        tenant_id=str(run.tenant_id),
        business_id=str(run.business_id),
        objective=run.objective or "",
        inputs=run.inputs or {},
        autonomy=_autonomy(business.autonomy_profile),
        guardrails=business.guardrails or {},
    )

    agent = agent_cls(llm=get_llm_router(), db=db)

    try:
        result = agent.run(ctx)
    except Exception as exc:  # defensive: never leave a run hanging
        run.status = "failed"
        run.finished_at = datetime.now(UTC)
        run.output = {"error": str(exc)}
        db.flush()
        log_activity(
            db,
            tenant_id=run.tenant_id,
            business_id=run.business_id,
            actor_type="agent",
            actor_id=agent_row.display_name,
            action="agent_run.failed",
            target_type="agent_run",
            target_id=str(run.id),
            summary=f"{agent_row.display_name} run failed: {exc}",
        )
        return run

    pending_task_id: str | None = None
    if result.requires_approval:
        task = Task(
            tenant_id=run.tenant_id,
            agent_run_id=run.id,
            title=(result.pending_action or {}).get("type", "Approval required"),
            type=(result.pending_action or {}).get("type", "approval"),
            agent_key=agent_row.key,
            risk_level="high",
            payload=result.pending_action or {},
            status="pending_approval",
            idempotency_key=f"{run.id}:approval",
        )
        db.add(task)
        db.flush()
        pending_task_id = str(task.id)

    run.status = "awaiting_approval" if result.requires_approval else "succeeded"
    run.progress = 0.6 if result.requires_approval else 1.0
    run.finished_at = None if result.requires_approval else datetime.now(UTC)
    run.model_used = result.model_used
    run.token_input = result.token_input
    run.token_output = result.token_output
    run.output = {
        "summary": result.summary,
        "artifacts": [a.get("type", "artifact") for a in result.artifacts],
        "artifacts_detail": result.artifacts,
        "recommendation": result.recommendation,
        "scores": result.scores,
        "pending_task_id": pending_task_id,
    }
    db.flush()

    log_activity(
        db,
        tenant_id=run.tenant_id,
        business_id=run.business_id,
        actor_type="agent",
        actor_id=agent_row.display_name,
        action=(
            "agent_run.completed"
            if not result.requires_approval
            else "agent_run.awaiting_approval"
        ),
        target_type="agent_run",
        target_id=str(run.id),
        summary=result.summary,
        meta={"recommendation": result.recommendation},
    )
    return run
