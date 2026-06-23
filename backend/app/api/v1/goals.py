"""Goals and OKR generation endpoints (nested under businesses)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.agents.base import AgentContext
from app.agents.registry import StrategyAgent
from app.api.deps import (
    CurrentPrincipal,
    get_business_or_404,
    get_current_principal,
    paginate,
)
from app.db import get_db
from app.llm.router import get_llm_router
from app.models.business import Business
from app.models.goal import OKR, Goal
from app.schemas.business import (
    GoalCreate,
    GoalOut,
    ObjectiveOut,
    OKRGenerateRequest,
    OKRGenerateResponse,
)
from app.schemas.common import Page
from app.services.activity import log_activity

router = APIRouter()


@router.post(
    "/{business_id}/goals", response_model=GoalOut, status_code=status.HTTP_201_CREATED
)
def create_goal(
    body: GoalCreate,
    business: Business = Depends(get_business_or_404),
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: Session = Depends(get_db),
) -> GoalOut:
    goal = Goal(
        tenant_id=business.tenant_id,
        business_id=business.id,
        title=body.title,
        description=body.description,
        metric=body.metric,
        target_value=body.target_value,
        target_date=body.target_date,
    )
    db.add(goal)
    db.flush()
    log_activity(
        db,
        tenant_id=business.tenant_id,
        business_id=business.id,
        actor_type="human",
        actor_id=str(principal.user.id),
        action="goal.created",
        target_type="goal",
        target_id=str(goal.id),
        summary=f"Created goal '{goal.title}'.",
    )
    return GoalOut.model_validate(goal)


@router.get("/{business_id}/goals", response_model=Page[GoalOut])
def list_goals(
    business: Business = Depends(get_business_or_404),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
) -> Page[GoalOut]:
    limit, offset = paginate(limit, offset)
    base = select(Goal).where(Goal.business_id == business.id)
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(
        base.order_by(Goal.created_at.desc()).limit(limit).offset(offset)
    ).scalars().all()
    return Page[GoalOut](
        items=[GoalOut.model_validate(g) for g in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/{business_id}/goals/{goal_id}/okrs",
    response_model=OKRGenerateResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def generate_okrs(
    goal_id: uuid.UUID,
    body: OKRGenerateRequest,
    business: Business = Depends(get_business_or_404),
    db: Session = Depends(get_db),
) -> OKRGenerateResponse:
    goal = db.get(Goal, goal_id)
    if goal is None or goal.business_id != business.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    agent = StrategyAgent(llm=get_llm_router(), db=db)
    ctx = AgentContext(
        tenant_id=str(business.tenant_id),
        business_id=str(business.id),
        objective=goal.title,
        inputs={
            "goal_title": goal.title,
            "metric": goal.metric,
            "target_value": float(goal.target_value) if goal.target_value is not None else 0,
            "horizon": body.horizon,
        },
    )
    objectives = agent.generate_okrs(ctx)

    out_objectives: list[ObjectiveOut] = []
    for obj in objectives:
        obj_id = uuid.uuid4()
        out_objectives.append(
            ObjectiveOut(id=obj_id, objective=obj["objective"], key_results=obj["key_results"])
        )
        for kr in obj["key_results"]:
            db.add(
                OKR(
                    tenant_id=business.tenant_id,
                    goal_id=goal.id,
                    objective=obj["objective"],
                    key_result=kr["kr"],
                    target_value=kr.get("target"),
                    current_value=kr.get("current", 0),
                )
            )
    db.flush()

    return OKRGenerateResponse(
        goal_id=goal.id,
        objectives=out_objectives,
        generated_by="StrategyAgent",
        generated_at=datetime.now(UTC),
    )
