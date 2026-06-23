"""Scoring formula tests — pure functions, no external services."""

from __future__ import annotations

from app.services import scoring


def test_clamp_bounds() -> None:
    assert scoring.clamp(-10) == 0.0
    assert scoring.clamp(150) == 100.0
    assert scoring.clamp(42) == 42.0


def test_risk_score_weights() -> None:
    # 0.30*100 + 0.25*0 + 0.25*0 + 0.20*0 = 30
    assert scoring.risk_score(100, 0, 0, 0) == 30.0
    # all max -> 100
    assert scoring.risk_score(100, 100, 100, 100) == 100.0
    # all zero -> 0
    assert scoring.risk_score(0, 0, 0, 0) == 0.0


def test_complexity_score_integration_normalization() -> None:
    # technical=0, execution=0, integration_count=10, norm=10 -> 0.30*100 = 30
    assert scoring.complexity_score(0, 0, 10, 10) == 30.0
    # integration_count beyond reference is clamped at 100
    assert scoring.complexity_score(0, 0, 50, 10) == 30.0
    # full mix
    assert scoring.complexity_score(100, 100, 10, 10) == 100.0


def test_potential_score_weights() -> None:
    # 0.30*100 = 30 when only market_size is maxed
    assert scoring.potential_score(100, 0, 0, 0, 0) == 30.0
    assert scoring.potential_score(100, 100, 100, 100, 100) == 100.0


def test_regulatory_bucket() -> None:
    assert scoring.regulatory_bucket("none") == 0.0
    assert scoring.regulatory_bucket("light") == 33.0
    assert scoring.regulatory_bucket("moderate") == 66.0
    assert scoring.regulatory_bucket("heavy") == 100.0
    assert scoring.regulatory_bucket("unknown") == 0.0


def test_saas_a_worked_example() -> None:
    """SaaS A from decision-hub.md: risk 35, complexity 60, potential 82 -> Build now."""
    rec = scoring.recommend(
        risk=35,
        complexity=60,
        potential=82,
        advisor_scores={
            "yc_pmf": 80,
            "tech_feasibility": 90,
            "moonshot_potential": 55,
            "global_scale_ease": 85,
            "monetization_strength": 80,
        },
    )
    assert rec.overall_call == "Build now"
    assert rec.ai_recommendation == "proceed"


def test_marketplace_c_parks() -> None:
    """Marketplace C: high potential + high moonshot but weak PMF/monetization -> Park."""
    rec = scoring.recommend(
        risk=70,
        complexity=85,
        potential=90,
        advisor_scores={
            "yc_pmf": 40,
            "tech_feasibility": 60,
            "moonshot_potential": 90,
            "global_scale_ease": 60,
            "monetization_strength": 35,
        },
    )
    assert rec.overall_call == "Park / R&D"
    assert rec.ai_recommendation == "park"


def test_kill_low_potential() -> None:
    rec = scoring.recommend(risk=20, complexity=20, potential=20)
    assert rec.overall_call == "Kill"
    assert rec.ai_recommendation == "kill"
