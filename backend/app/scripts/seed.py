"""Idempotent seed script: demo tenant, founder, business, goals, agent roster,
and a sample 3-option decision (SaaS A / Info Product B / Marketplace C).

Run with: python -m app.scripts.seed
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.agents.registry import roster_metadata
from app.core.security import hash_password
from app.db import SessionLocal
from app.models.agent import Agent
from app.models.business import Business
from app.models.decision import Decision, DecisionOption
from app.models.goal import Goal
from app.models.tenant import Tenant
from app.models.user import Membership, User

FOUNDER_EMAIL = "founder@myuno.dev"
FOUNDER_PASSWORD = "ChangeMe123!"

# (name, risk, complexity, potential, time_to_impact, capital_cents, advisor, justification, recommended)
_SAMPLE_OPTIONS = [
    (
        "SaaS A",
        35,
        60,
        82,
        "3-6 months",
        500_000,
        {
            "yc_pmf": 80,
            "tech_feasibility": 90,
            "moonshot_potential": 55,
            "global_scale_ease": 85,
            "monetization_strength": 80,
            "overall_call": "Build now",
        },
        "Best balance of high potential (82) and moderate risk (35); strong PMF, "
        "high feasibility, strong monetization, easy to scale globally.",
        True,
    ),
    (
        "Info Product B",
        20,
        30,
        60,
        "1-2 months",
        100_000,
        {
            "yc_pmf": 65,
            "tech_feasibility": 90,
            "moonshot_potential": 30,
            "global_scale_ease": 60,
            "monetization_strength": 60,
            "overall_call": "Proceed (starter)",
        },
        "Lowest risk and complexity, fastest time to impact and cheapest; "
        "capped upside but an excellent low-risk cash/learning starter.",
        False,
    ),
    (
        "Marketplace C",
        70,
        85,
        90,
        "6-12 months",
        1_000_000,
        {
            "yc_pmf": 40,
            "tech_feasibility": 60,
            "moonshot_potential": 90,
            "global_scale_ease": 60,
            "monetization_strength": 35,
            "overall_call": "Park / R&D",
        },
        "Highest potential and moonshot upside but risk 70, complexity 85, $10k+ "
        "capital and weak near-term monetization. Park for later R&D.",
        False,
    ),
]


def _get_or_create_tenant(db: Session) -> Tenant:
    tenant = db.execute(
        select(Tenant).where(Tenant.name == "MyUNO Demo Workspace")
    ).scalar_one_or_none()
    if tenant is None:
        tenant = Tenant(name="MyUNO Demo Workspace", plan_tier="solo_pro", task_quota_month=1000)
        db.add(tenant)
        db.flush()
    return tenant


def _get_or_create_founder(db: Session, tenant: Tenant) -> User:
    user = db.execute(
        select(User).where(func.lower(User.email) == FOUNDER_EMAIL)
    ).scalar_one_or_none()
    if user is None:
        user = User(
            email=FOUNDER_EMAIL,
            full_name="Demo Founder",
            password_hash=hash_password(FOUNDER_PASSWORD),
            default_autonomy_profile="guided",
        )
        db.add(user)
        db.flush()
    membership = db.execute(
        select(Membership).where(
            Membership.tenant_id == tenant.id, Membership.user_id == user.id
        )
    ).scalar_one_or_none()
    if membership is None:
        db.add(Membership(tenant_id=tenant.id, user_id=user.id, role="owner"))
        db.flush()
    return user


def _get_or_create_business(db: Session, tenant: Tenant) -> Business:
    business = db.execute(
        select(Business).where(
            Business.tenant_id == tenant.id, Business.name == "InboxZero SaaS"
        )
    ).scalar_one_or_none()
    if business is None:
        business = Business(
            tenant_id=tenant.id,
            name="InboxZero SaaS",
            model_template="b2b_saas",
            description="AI inbox triage for solo consultants.",
            stage="validate",
            autonomy_profile="guided",
            guardrails={"ad_spend_daily_cap_cents": 5000, "require_deploy_approval": True},
            brand_voice="Direct, friendly, founder-to-founder.",
        )
        db.add(business)
        db.flush()
    return business


def _seed_goals(db: Session, tenant: Tenant, business: Business) -> None:
    desired = [
        ("Profitably reach $10k MRR in 12 months", "mrr", 10000, date(2027, 6, 23)),
        ("Validate demand with 3 paying customers", "count", 3, date(2026, 9, 1)),
    ]
    for title, metric, target, target_date in desired:
        exists = db.execute(
            select(Goal).where(Goal.business_id == business.id, Goal.title == title)
        ).scalar_one_or_none()
        if exists is None:
            db.add(
                Goal(
                    tenant_id=tenant.id,
                    business_id=business.id,
                    title=title,
                    metric=metric,
                    target_value=target,
                    target_date=target_date,
                )
            )
    db.flush()


def _seed_agents(db: Session) -> int:
    count = 0
    for meta in roster_metadata():
        exists = db.execute(
            select(Agent).where(Agent.key == meta["key"])
        ).scalar_one_or_none()
        if exists is None:
            db.add(
                Agent(
                    key=meta["key"],
                    display_name=meta["agent"],
                    category=meta["category"],
                    description=meta["description"],
                    default_model=meta["default_model"],
                    min_tier=meta["min_tier"],
                    tool_scopes={"integrations": meta["required_integrations"]},
                )
            )
            count += 1
    db.flush()
    return count


def _seed_decision(db: Session, tenant: Tenant, business: Business) -> None:
    decision = db.execute(
        select(Decision).where(
            Decision.business_id == business.id, Decision.title == "Which idea to build first?"
        )
    ).scalar_one_or_none()
    if decision is not None:
        return
    decision = Decision(
        tenant_id=tenant.id,
        business_id=business.id,
        decision_type="idea",
        title="Which idea to build first?",
        context="Three candidate ideas evaluated by IdeaValidationAgent + advisor panel.",
        ai_recommendation="proceed",
        overall_call="Build now",
        status="ready",
    )
    db.add(decision)
    db.flush()
    for (
        name,
        risk,
        complexity,
        potential,
        tti,
        capital,
        advisor,
        justification,
        recommended,
    ) in _SAMPLE_OPTIONS:
        opt = DecisionOption(
            tenant_id=tenant.id,
            decision_id=decision.id,
            option_name=name,
            risk_score=risk,
            complexity_score=complexity,
            potential_score=potential,
            time_to_impact=tti,
            capital_required_cents=capital,
            advisor_scores=advisor,
            ai_justification=justification,
            is_recommended=recommended,
        )
        db.add(opt)
    db.flush()


def main() -> None:
    db = SessionLocal()
    try:
        tenant = _get_or_create_tenant(db)
        _get_or_create_founder(db, tenant)
        business = _get_or_create_business(db, tenant)
        _seed_goals(db, tenant, business)
        agents_added = _seed_agents(db)
        _seed_decision(db, tenant, business)
        db.commit()
        print(
            f"Seed complete: tenant={tenant.id} business={business.id} "
            f"founder={FOUNDER_EMAIL} agents_added={agents_added}"
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
