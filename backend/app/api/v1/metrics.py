"""Metrics and exit-readiness endpoints."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_business_or_404
from app.db import get_db
from app.models.business import Business
from app.models.metric import ExitReadiness, Metric
from app.schemas.metric import (
    ExitReadinessComponents,
    ExitReadinessResponse,
    MetricsResponse,
)

router = APIRouter()


def _latest_metric(db: Session, business_id, key: str) -> float:
    row = db.execute(
        select(Metric)
        .where(Metric.business_id == business_id, Metric.metric_key == key)
        .order_by(Metric.recorded_at.desc())
    ).scalars().first()
    return float(row.value) if row is not None else 0.0


@router.get("/{business_id}/metrics", response_model=MetricsResponse)
def get_metrics(
    business: Business = Depends(get_business_or_404),
    db: Session = Depends(get_db),
    period: str = Query(default="30d"),
) -> MetricsResponse:
    mrr = _latest_metric(db, business.id, "mrr")
    churn = _latest_metric(db, business.id, "churn_rate")
    cac = _latest_metric(db, business.id, "cac")
    ltv = _latest_metric(db, business.id, "ltv")
    signups = _latest_metric(db, business.id, "signups")
    nps = _latest_metric(db, business.id, "nps")
    mrr_growth = _latest_metric(db, business.id, "mrr_growth_pct")

    return MetricsResponse(
        business_id=business.id,
        period=period,
        mrr=mrr,
        mrr_growth_pct=mrr_growth,
        churn_rate_pct=churn,
        cac=cac,
        ltv=ltv,
        ltv_cac_ratio=round(ltv / cac, 2) if cac else 0,
        signups=signups,
        nps=nps,
        updated_at=datetime.now(UTC),
    )


@router.get("/{business_id}/exit-readiness", response_model=ExitReadinessResponse)
def get_exit_readiness(
    business: Business = Depends(get_business_or_404),
    db: Session = Depends(get_db),
) -> ExitReadinessResponse:
    row = db.execute(
        select(ExitReadiness).where(ExitReadiness.business_id == business.id)
    ).scalars().first()

    if row is None:
        # Default zeroed assessment when none has been computed yet.
        return ExitReadinessResponse(
            business_id=business.id,
            exit_readiness_score=0,
            components=ExitReadinessComponents(
                financials=0, metrics=0, documentation=0, operational_stability=0
            ),
            recommendation="Run the ExitPlanningAgent to compute an initial assessment.",
            updated_at=datetime.now(UTC),
        )

    recommendation = (
        "Exit-ready: begin acquirer outreach when desired."
        if row.overall_score >= 75
        else "Improve documentation and data room before outreach."
    )
    return ExitReadinessResponse(
        business_id=business.id,
        exit_readiness_score=row.overall_score,
        components=ExitReadinessComponents(
            financials=row.financials_score,
            metrics=row.metrics_score,
            documentation=row.documentation_score,
            operational_stability=row.operational_stability_score,
        ),
        recommendation=recommendation,
        updated_at=row.assessed_at,
    )
