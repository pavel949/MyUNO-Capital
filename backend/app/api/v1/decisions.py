"""Decision Hub endpoints: create decision (+score options), list, detail, select."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import (
    CurrentPrincipal,
    get_business_or_404,
    get_current_principal,
    paginate,
)
from app.db import get_db
from app.models.business import Business
from app.models.decision import Decision, DecisionOption
from app.schemas.common import Page
from app.schemas.decision import (
    DecisionCreate,
    DecisionCreated,
    DecisionDetail,
    DecisionSelectRequest,
    DecisionSelectResponse,
    OptionDetail,
    OptionListItem,
)
from app.services import scoring
from app.services.activity import log_activity

router = APIRouter()


def _norm(value, default: float) -> float:
    try:
        return scoring.clamp(float(value))
    except (TypeError, ValueError):
        return default


def _capital_label(cents: int | None) -> str | None:
    if cents is None:
        return None
    dollars = cents / 100
    if dollars < 1000:
        return f"${int(dollars)}"
    return f"${int(dollars / 1000)}k"


def _score_option(option_name: str, factors: dict) -> dict:
    """Compute Risk/Complexity/Potential + advisor scores for one option."""
    risk = scoring.risk_score(
        competition=_norm(factors.get("competition"), 55),
        regulatory=_norm(factors.get("regulatory"), 33),
        capital=_norm(factors.get("capital"), 40),
        platform_dependence=_norm(factors.get("platform_dependence"), 30),
    )
    complexity = scoring.complexity_score(
        technical=_norm(factors.get("technical"), 55),
        execution=_norm(factors.get("execution"), 45),
        integration_count=float(factors.get("integration_count", 4)),
        normalization_factor=float(factors.get("normalization_factor", 10)),
    )
    potential = scoring.potential_score(
        market_size=_norm(factors.get("market_size"), 70),
        trend=_norm(factors.get("trend"), 70),
        pricing_power=_norm(factors.get("pricing_power"), 65),
        scalability=_norm(factors.get("scalability"), 75),
        founder_fit=_norm(factors.get("founder_fit"), 70),
    )
    advisor = {
        "yc_pmf": int(round(scoring.clamp(potential * 0.9 + 5))),
        "tech_feasibility": int(round(scoring.clamp(100 - complexity * 0.6))),
        "moonshot_potential": int(round(scoring.clamp(potential * 0.7))),
        "global_scale_ease": int(round(scoring.clamp(75 - risk * 0.2))),
        "monetization_strength": int(round(scoring.clamp(potential * 0.85 + 5))),
    }
    rec = scoring.recommend(risk, complexity, potential, advisor)
    return {
        "risk": int(round(risk)),
        "complexity": int(round(complexity)),
        "potential": int(round(potential)),
        "advisor_scores": advisor,
        "overall_call": rec.overall_call,
        "ai_recommendation": rec.ai_recommendation,
        "justification": rec.rationale,
        "time_to_impact": factors.get("time_to_impact"),
        "capital_required_cents": factors.get("capital_required_cents"),
    }


@router.post(
    "/{business_id}/decisions",
    response_model=DecisionCreated,
    status_code=status.HTTP_201_CREATED,
)
def create_decision(
    body: DecisionCreate,
    business: Business = Depends(get_business_or_404),
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: Session = Depends(get_db),
) -> DecisionCreated:
    decision = Decision(
        tenant_id=business.tenant_id,
        business_id=business.id,
        decision_type=body.type,
        title=body.title,
        context=body.context,
        status="scoring",
    )
    db.add(decision)
    db.flush()

    best_option_id: uuid.UUID | None = None
    best_potential = -1
    best_call = None
    best_rec = None
    for opt in body.options:
        scored = _score_option(opt.name, opt.factors)
        option = DecisionOption(
            tenant_id=business.tenant_id,
            decision_id=decision.id,
            option_name=opt.name,
            risk_score=scored["risk"],
            complexity_score=scored["complexity"],
            potential_score=scored["potential"],
            time_to_impact=scored["time_to_impact"],
            capital_required_cents=scored["capital_required_cents"],
            advisor_scores={
                **scored["advisor_scores"],
                "overall_call": scored["overall_call"],
            },
            ai_justification=scored["justification"],
        )
        db.add(option)
        db.flush()
        if scored["potential"] > best_potential:
            best_potential = scored["potential"]
            best_option_id = option.id
            best_call = scored["overall_call"]
            best_rec = scored["ai_recommendation"]

    if best_option_id is not None:
        for option in db.execute(
            select(DecisionOption).where(DecisionOption.decision_id == decision.id)
        ).scalars():
            option.is_recommended = option.id == best_option_id
        decision.overall_call = best_call
        decision.ai_recommendation = best_rec
    decision.status = "ready"
    db.flush()

    log_activity(
        db,
        tenant_id=business.tenant_id,
        business_id=business.id,
        actor_type="agent",
        actor_id="IdeaValidationAgent",
        action="decision.created",
        target_type="decision",
        target_id=str(decision.id),
        summary=f"Scored {len(body.options)} options for '{decision.title}'.",
    )

    return DecisionCreated(
        id=decision.id,
        business_id=business.id,
        title=decision.title,
        type=decision.decision_type,
        status=decision.status,
        created_at=decision.created_at,
    )


def _load_decision(db: Session, business: Business, decision_id: uuid.UUID) -> Decision:
    decision = db.get(Decision, decision_id)
    if decision is None or decision.business_id != business.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")
    return decision


@router.get(
    "/{business_id}/decisions/{decision_id}/options", response_model=Page[OptionListItem]
)
def list_options(
    decision_id: uuid.UUID,
    business: Business = Depends(get_business_or_404),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
) -> Page[OptionListItem]:
    limit, offset = paginate(limit, offset)
    _load_decision(db, business, decision_id)
    rows = db.execute(
        select(DecisionOption)
        .where(DecisionOption.decision_id == decision_id)
        .order_by(DecisionOption.potential_score.desc())
    ).scalars().all()
    items = [
        OptionListItem(
            id=o.id,
            name=o.option_name,
            risk=o.risk_score,
            complexity=o.complexity_score,
            potential=o.potential_score,
            time_to_impact=o.time_to_impact,
            capital_required=_capital_label(o.capital_required_cents),
            ai_recommendation=o.advisor_scores.get("overall_call"),
        )
        for o in rows
    ]
    return Page[OptionListItem](
        items=items[offset : offset + limit], total=len(items), limit=limit, offset=offset
    )


@router.get("/{business_id}/decisions/{decision_id}", response_model=DecisionDetail)
def get_decision(
    decision_id: uuid.UUID,
    business: Business = Depends(get_business_or_404),
    db: Session = Depends(get_db),
) -> DecisionDetail:
    decision = _load_decision(db, business, decision_id)
    rows = db.execute(
        select(DecisionOption)
        .where(DecisionOption.decision_id == decision_id)
        .order_by(DecisionOption.potential_score.desc())
    ).scalars().all()
    options = [
        OptionDetail(
            id=o.id,
            name=o.option_name,
            risk=o.risk_score,
            complexity=o.complexity_score,
            potential=o.potential_score,
            advisor_scores={k: v for k, v in o.advisor_scores.items() if k != "overall_call"},
            overall_call=o.advisor_scores.get("overall_call"),
            justification=o.ai_justification,
            is_recommended=o.is_recommended,
        )
        for o in rows
    ]
    return DecisionDetail(
        id=decision.id,
        title=decision.title,
        status=decision.status,
        type=decision.decision_type,
        ai_recommendation=decision.ai_recommendation,
        overall_call=decision.overall_call,
        options=options,
    )


@router.post(
    "/{business_id}/decisions/{decision_id}/select", response_model=DecisionSelectResponse
)
def select_option(
    decision_id: uuid.UUID,
    body: DecisionSelectRequest,
    business: Business = Depends(get_business_or_404),
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: Session = Depends(get_db),
) -> DecisionSelectResponse:
    decision = _load_decision(db, business, decision_id)
    option = db.get(DecisionOption, body.option_id)
    if option is None or option.decision_id != decision.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found")

    decided_at = datetime.now(UTC)
    decision.chosen_option_id = option.id
    decision.status = "decided"
    decision.decided_by = principal.user.id
    decision.decided_at = decided_at
    db.flush()

    log_activity(
        db,
        tenant_id=business.tenant_id,
        business_id=business.id,
        actor_type="human",
        actor_id=str(principal.user.id),
        action="decision.decided",
        target_type="decision",
        target_id=str(decision.id),
        summary=f"Selected '{option.option_name}'. {body.note or ''}".strip(),
        meta={
            "option_id": str(option.id),
            "scores": {
                "risk": option.risk_score,
                "complexity": option.complexity_score,
                "potential": option.potential_score,
            },
            "note": body.note,
        },
    )

    return DecisionSelectResponse(
        id=decision.id,
        status=decision.status,
        selected_option_id=option.id,
        decided_at=decided_at,
    )
