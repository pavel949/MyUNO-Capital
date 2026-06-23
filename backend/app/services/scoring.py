"""Decision Hub scoring formulas (project.md §11.3 / decision-hub.md §4-5).

Pure Python, no DB access. All input factors are normalized to 0-100 before the
weighted sum, so every score lands in 0-100.
"""

from __future__ import annotations

from dataclasses import dataclass

# Default reference "high" integration count used to normalize IntegrationCount.
DEFAULT_NORMALIZATION_FACTOR = 10.0


def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    """Clamp a value into [lo, hi]."""
    return max(lo, min(hi, x))


def risk_score(
    competition: float,
    regulatory: float,
    capital: float,
    platform_dependence: float,
) -> float:
    """Risk Score (0-100). Higher = riskier. All inputs pre-normalized to 0-100.

    0.30*CompetitionIntensity + 0.25*RegulatoryRisk + 0.25*CapitalRequirement
    + 0.20*PlatformDependence
    """
    return clamp(
        0.30 * competition
        + 0.25 * regulatory
        + 0.25 * capital
        + 0.20 * platform_dependence
    )


def complexity_score(
    technical: float,
    execution: float,
    integration_count: float,
    normalization_factor: float = DEFAULT_NORMALIZATION_FACTOR,
) -> float:
    """Complexity Score (0-100). Higher = more complex.

    0.40*TechnicalComplexity + 0.30*ExecutionComplexity
    + 0.30*(IntegrationCount / NormalizationFactor)
    """
    factor = normalization_factor if normalization_factor else DEFAULT_NORMALIZATION_FACTOR
    integration = clamp(100.0 * integration_count / factor)
    return clamp(
        0.40 * technical
        + 0.30 * execution
        + 0.30 * integration
    )


def potential_score(
    market_size: float,
    trend: float,
    pricing_power: float,
    scalability: float,
    founder_fit: float,
) -> float:
    """Potential Score (0-100). Higher = more upside.

    0.30*MarketSize + 0.20*TrendDirection + 0.20*PricingPower
    + 0.15*Scalability + 0.15*FounderFit
    """
    return clamp(
        0.30 * market_size
        + 0.20 * trend
        + 0.20 * pricing_power
        + 0.15 * scalability
        + 0.15 * founder_fit
    )


# --- Regulatory-risk bucket helper (categorical -> 0/33/66/100) ------------
_REGULATORY_BUCKETS = {"none": 0.0, "light": 33.0, "moderate": 66.0, "heavy": 100.0}


def regulatory_bucket(level: str) -> float:
    """Map a categorical regulatory level to its normalized 0-100 value."""
    return _REGULATORY_BUCKETS.get(level.lower().strip(), 0.0)


@dataclass
class OverallRecommendation:
    """Headline verdict combining base scores and (optionally) advisor scores."""

    overall_call: str  # "Build now" / "Proceed with constraints" / "Park / R&D" / "Kill"
    ai_recommendation: str  # taxonomy: proceed / proceed_with_constraints / park / kill
    rationale: str


def recommend(
    risk: float,
    complexity: float,
    potential: float,
    advisor_scores: dict[str, float] | None = None,
) -> OverallRecommendation:
    """Combine base scores + advisor panel into an Overall Call.

    Heuristics mirror decision-hub.md §6:
      - High Potential + healthy advisors + manageable Risk/Complexity -> Build now.
      - High Moonshot but weak PMF/Monetization -> Park / R&D.
      - Strong upside gated by one or two risks -> Proceed with constraints.
      - Low Potential or fatal Risk -> Kill.
    """
    advisors = advisor_scores or {}
    pmf = float(advisors.get("yc_pmf", advisors.get("yc_pmf_score", 50)))
    monetization = float(advisors.get("monetization_strength", 50))
    moonshot = float(advisors.get("moonshot_potential", 50))

    # Fatal: little upside or overwhelming risk.
    if potential < 35 or risk >= 85:
        return OverallRecommendation(
            "Kill",
            "kill",
            f"Potential ({potential:.0f}) too low or risk ({risk:.0f}) prohibitive.",
        )

    # Build now: strong, well-supported, manageable downside.
    if (
        potential >= 70
        and risk <= 50
        and complexity <= 75
        and pmf >= 60
        and monetization >= 55
    ):
        return OverallRecommendation(
            "Build now",
            "proceed",
            (
                f"High potential ({potential:.0f}) with manageable risk ({risk:.0f}); "
                f"PMF and monetization signals are healthy."
            ),
        )

    # Park / R&D: visionary but unproven near-term.
    if moonshot >= 70 and (pmf < 55 or monetization < 50):
        return OverallRecommendation(
            "Park / R&D",
            "park",
            (
                f"Strong long-term upside (moonshot {moonshot:.0f}) but weak near-term PMF/"
                f"monetization; revisit after cash-flow is established."
            ),
        )

    # Default: proceed with constraints (strong upside gated by risk/complexity).
    return OverallRecommendation(
        "Proceed with constraints",
        "proceed_with_constraints",
        (
            f"Promising potential ({potential:.0f}) gated by risk ({risk:.0f}) / "
            f"complexity ({complexity:.0f}); proceed within explicit guardrails."
        ),
    )
