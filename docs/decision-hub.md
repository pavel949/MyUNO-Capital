# Decision Hub — MyUNO Capital

> The central place to compare options and make decisions with **data, not gut feeling**.

**Related docs:** [Agents reference](./agents.md) · [Data model](./data-model.md) · [Project overview](../project.md)

---

## 1. What the Decision Hub Is (and Why)

Solo founders make high-stakes calls alone — which idea to pursue, which feature to build, which channel to bet on, how to price, which stack to use. Without a co-founder to challenge assumptions, these calls are often made on instinct, late at night, with incomplete information.

The **Decision Hub** replaces gut feeling with a structured, repeatable process:

1. Every major decision is framed as a set of **options**.
2. Agents gather data and run experiments to **score** each option on common dimensions.
3. The **Elite Advisor & Accelerator Layer** adds multi-angle "elite" scores and recommendations.
4. The founder sees scores, justifications, and an AI recommendation side-by-side — then **chooses**.
5. The decision and its reasoning are **logged** to the activity log for trust, debugging, and exit due diligence.

The founder always makes the final call. The Hub makes that call faster, better-informed, and auditable.

---

## 2. The Options Table Model

Every decision is represented as an **Options Table**: a set of competing options, each scored on the same dimensions.

### Option Types

| Option Type | Example | Primary scoring agents |
|-------------|---------|------------------------|
| **Idea** | "AI bookkeeping for freelancers" vs "Niche e-commerce brand" | [IdeaValidationAgent](./agents.md#ideavalidationagent) + all advisors |
| **Feature** | "Build SSO" vs "Build mobile app" | [ProductManagerAgent](./agents.md#productmanageragent) |
| **Channel** | "Google Ads" vs "Content/SEO" vs "Cold outreach" | [MarketingStrategyAgent](./agents.md#marketingstrategyagent) |
| **Pricing** | "$29 flat" vs "$19/$49/$99 tiers" | [Fintech/Product Excellence Agent](./agents.md#fintechproduct-excellence-agent-tinkoff-like) |
| **Tech Stack** | "No-code (Bubble)" vs "Full code (FastAPI + Next.js)" | [ArchitectAgent](./agents.md#architectagent) |

### Scored Dimensions (per option)

| Dimension | Scale | Meaning |
|-----------|-------|---------|
| **Risk Score** | 0–100 | Higher = more risky. |
| **Complexity Score** | 0–100 | Higher = more complex to execute. |
| **Potential Score** | 0–100 | Higher = more upside. |
| **Time to Impact** | duration | Estimated time to first meaningful result. |
| **Capital Required** | currency range | Rough cost to reach the first milestones. |

The canonical example Options Table for an idea decision:

| Option Type | Option Name    | Risk | Complexity | Potential | Time to Impact | Capital Required | AI Recommendation | Your Choice |
|-------------|----------------|------|------------|-----------|----------------|------------------|-------------------|-------------|
| Idea        | SaaS A         | 35   | 60         | 82        | 3–6 months     | $3k–$5k          | Strong candidate  | [Select]    |
| Idea        | Info Product B | 20   | 30         | 60        | 1–2 months     | $500–$1k         | Good starter      | [Select]    |
| Idea        | Marketplace C  | 70   | 85         | 90        | 6–12 months    | $10k+            | Too heavy now     | [Select]    |

---

## 3. Scoring Dimensions in Depth

The three numeric scores (Risk, Complexity, Potential) are each computed from weighted input factors. **All input factors are normalized to a 0–100 scale internally** before the weighted sum is applied, so every score lands in the 0–100 range.

### Normalization

Each raw input factor is mapped to 0–100 before weighting. Common approaches:

- **Categorical → bucket** — e.g., RegulatoryRisk: `none=0, light=33, moderate=66, heavy=100`.
- **Bounded numeric → min–max** — e.g., `IntegrationCount` divided by a `NormalizationFactor` (a reference "high" count, e.g. 10) and clamped to 100.
- **Ratio/index → rescaled** — e.g., MarketSize mapped against a reference TAM band to a 0–100 index.

This guarantees each factor contributes proportionally to its weight, regardless of its native units.

---

## 4. Scoring Formulas

Reproduced exactly from `project.md` section 11.3:

```text
Risk Score (0–100) ≈
  0.30 × CompetitionIntensity +
  0.25 × RegulatoryRisk +
  0.25 × CapitalRequirement +
  0.20 × PlatformDependence

Complexity Score (0–100) ≈
  0.40 × TechnicalComplexity +
  0.30 × ExecutionComplexity +
  0.30 × IntegrationCount / NormalizationFactor

Potential Score (0–100) ≈
  0.30 × MarketSize +
  0.20 × TrendDirection +
  0.20 × PricingPower +
  0.15 × Scalability +
  0.15 × FounderFit
```

*(All inputs normalized to 0–100 internally.)*

### Input factors explained

**Risk Score**

| Factor | Weight | What it captures | Normalized as |
|--------|--------|------------------|---------------|
| `CompetitionIntensity` | 0.30 | How crowded and entrenched the market is. | 0 = blue ocean, 100 = saturated with strong incumbents. |
| `RegulatoryRisk` | 0.25 | Legal/regulatory exposure (data, finance, health). | Bucketed: none/light/moderate/heavy → 0/33/66/100. |
| `CapitalRequirement` | 0.25 | How much money is at risk to reach first milestones. | Spend band mapped to 0–100 (e.g. <$1k≈10, $10k+≈90). |
| `PlatformDependence` | 0.20 | Reliance on a third party that could change terms or cut access. | 0 = independent, 100 = fully dependent on one platform. |

**Complexity Score**

| Factor | Weight | What it captures | Normalized as |
|--------|--------|------------------|---------------|
| `TechnicalComplexity` | 0.40 | Difficulty of the core technology/build. | 0 = no-code template, 100 = novel R&D. |
| `ExecutionComplexity` | 0.30 | Operational difficulty of running it (logistics, support, multi-sided). | 0 = simple, 100 = highly operationally intensive. |
| `IntegrationCount / NormalizationFactor` | 0.30 | Number of external integrations required, normalized against a reference high count. | `min(100, 100 × IntegrationCount / NormalizationFactor)`. |

**Potential Score**

| Factor | Weight | What it captures | Normalized as |
|--------|--------|------------------|---------------|
| `MarketSize` | 0.30 | Size of the addressable opportunity. | TAM band rescaled to 0–100. |
| `TrendDirection` | 0.20 | Whether the market is growing or shrinking. | 0 = declining, 50 = flat, 100 = strong tailwind. |
| `PricingPower` | 0.20 | Ability to charge well and resist discounting. | 0 = commodity, 100 = premium/willingness-to-pay. |
| `Scalability` | 0.15 | How well it grows without linear cost. | 0 = service-bound, 100 = pure software leverage. |
| `FounderFit` | 0.15 | Match to the founder's skills, network, and interest. | 0 = no fit, 100 = ideal fit. |

> **Convention:** Risk and Complexity are "lower is better" (higher = more risk/complexity), while Potential is "higher is better." The AI recommendation balances all three plus advisor scores — see [Overall Call](#6-advisor-integration--the-overall-call).

---

## 5. Reference Implementation

A minimal Python reference (canonical stack: Python 3.12) of the formulas above:

```python
def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def risk_score(competition, regulatory, capital, platform_dependence) -> float:
    """All inputs are pre-normalized to 0–100."""
    return clamp(
        0.30 * competition
        + 0.25 * regulatory
        + 0.25 * capital
        + 0.20 * platform_dependence
    )


def complexity_score(technical, execution, integration_count,
                     normalization_factor: float = 10.0) -> float:
    integration = clamp(100.0 * integration_count / normalization_factor)
    return clamp(
        0.40 * technical
        + 0.30 * execution
        + 0.30 * integration
    )


def potential_score(market_size, trend, pricing_power,
                   scalability, founder_fit) -> float:
    return clamp(
        0.30 * market_size
        + 0.20 * trend
        + 0.20 * pricing_power
        + 0.15 * scalability
        + 0.15 * founder_fit
    )
```

---

## 6. Advisor Integration & the Overall Call

For major decisions (idea choice, market selection, funding vs bootstrapping, exit timing), the [Elite Advisor & Accelerator Layer](./agents.md#12-elite-advisor--accelerator-layer-section-44) layers five additional dimensions on top of the base scores. Each advisor returns a **0–100 score**, a short narrative justification, and a recommendation from the taxonomy **Proceed / Proceed with constraints / Park / Kill**.

| Advisor dimension | Source agent | Captures |
|-------------------|--------------|----------|
| **YC PMF Score** | [YC Accelerator Agent](./agents.md#yc-accelerator-agent) | Product-market fit signal (retention, engagement, revenue). |
| **Tech Feasibility** | [Deep Tech Validation Agent](./agents.md#deep-tech-validation-agent-mit-like) | Technical feasibility vs state-of-the-art and prior art. |
| **Moonshot Potential** | [Moonshot Strategy Agent](./agents.md#moonshot-strategy-agent-elon-like) | 10x / long-term upside under first-principles reasoning. |
| **Global Scale Ease** | [Global Ecosystem Builder Agent](./agents.md#global-ecosystem-builder-agent-jack-malike) | Ease of expanding across markets (size, regulation, localization). |
| **Monetization Strength** | [Fintech/Product Excellence Agent](./agents.md#fintechproduct-excellence-agent-tinkoff-like) | Pricing power and unit-economics health (CAC, LTV, payback). |

### The Overall Call

The Hub combines the base scores and advisor panel into an **Overall Call** — a plain-language verdict such as **Build now**, **Park / R&D**, **Proceed with constraints**, or **Kill**. Conceptually:

- **High Potential + healthy advisor scores + manageable Risk/Complexity** → *Build now*.
- **High Moonshot Potential but weak PMF/Monetization or unproven feasibility** → *Park / R&D*.
- **Strong upside gated by one or two risks** → *Proceed with constraints* (with the specific constraints listed).
- **Low Potential or fatal Risk** → *Kill*.

The founder retains the final decision — now justified by multi-angle reasoning.

---

## 7. Worked Example: Three Ideas

A founder runs three candidate ideas through the Decision Hub.

### Step 1 — Options generated, base scores computed

[IdeaValidationAgent](./agents.md#ideavalidationagent) researches markets and runs cheap experiments, producing:

| Option Type | Option Name    | Risk | Complexity | Potential | Time to Impact | Capital Required | AI Recommendation |
|-------------|----------------|------|------------|-----------|----------------|------------------|-------------------|
| Idea        | SaaS A         | 35   | 60         | 82        | 3–6 months     | $3k–$5k          | Strong candidate  |
| Idea        | Info Product B | 20   | 30         | 60        | 1–2 months     | $500–$1k         | Good starter      |
| Idea        | Marketplace C  | 70   | 85         | 90        | 6–12 months    | $10k+            | Too heavy now     |

### Step 2 — Advisor panel scores each idea

| Option        | YC PMF Score | Tech Feasibility | Moonshot Potential | Global Scale Ease | Monetization Strength | Overall Call          |
|---------------|--------------|------------------|--------------------|-------------------|------------------------|-----------------------|
| SaaS A        | 80/100       | High             | Medium             | High              | Strong                 | **Build now**         |
| Info Product B| 65/100       | High             | Low                | Medium            | Medium                 | **Proceed (starter)** |
| Marketplace C | 40/100       | Medium           | Very High          | Medium            | Weak                   | **Park / R&D**        |

### Step 3 — Reasoning surfaced to the founder

- **SaaS A** — Best balance: high Potential (82) with only moderate Risk (35). Advisors agree: strong PMF signal, high feasibility, strong monetization, easy to scale globally. *Build now.*
- **Info Product B** — Lowest Risk (20) and Complexity (30), fastest Time to Impact (1–2 months) and cheapest ($500–$1k). Upside is capped (Potential 60, low Moonshot). An excellent low-risk *starter* to generate cash and learning.
- **Marketplace C** — Highest Potential (90) and Moonshot Potential (Very High), but Risk 70, Complexity 85, $10k+ capital, and weak near-term monetization. The Fintech advisor flags poor early unit economics; the YC advisor flags weak PMF signal. *Park / R&D* — revisit after SaaS A produces cash flow.

### Step 4 — Recommendation and choice

The Hub's headline recommendation: **Start with SaaS A; optionally run Info Product B in parallel as a low-cost cash/learning bet; park Marketplace C for later R&D.**

The founder selects **SaaS A**. The choice, all scores, advisor justifications, and the founder's selection are written to the activity log.

---

## 8. The Decision Workflow

```text
1. Generate options       →  System generates/imports options (Idea, Feature, Channel,
                             Pricing, Tech Stack).
2. Gather data / run       →  Functional agents research and run experiments; advisor
   experiments               agents prepare to score.
3. Compute scores          →  Risk / Complexity / Potential per the formulas; advisors add
                             5 dimensions + recommendations (Proceed / Proceed with
                             constraints / Park / Kill).
4. Show recommendation     →  Decision Hub presents the Options Table with scores,
                             justifications, the AI recommendation, and the Overall Call.
5. Founder selects         →  Founder reviews and confirms a choice (or overrides).
6. Log decision + reasoning→  Decision, scores, advisor justifications, AI recommendation,
                             and the chosen option are persisted to the global activity log.
```

This mirrors the lifecycle Advisor Checkpoints in `project.md` section 11.1 (e.g., Ideation → Deep Tech + Moonshot; Validate → YC + Fintech).

---

## 9. Persistence

Decisions and their options are persisted relationally and to the global activity log so they can be audited later (trust, debugging, and exit due diligence). See [data-model.md](./data-model.md) for the full schema:

- **`decisions`** — one row per decision: type, status, the chosen option, the AI recommendation / Overall Call, the human reasoning, and a link to the activity-log entry.
- **`decision_options`** — one row per option within a decision: option type and name, the base scores (Risk/Complexity/Potential), Time to Impact, Capital Required, the five advisor scores, per-advisor recommendations and justifications, and a `chosen` flag.

Scores and justifications are stored at decision time (point-in-time snapshot) so the record reflects what was known when the founder decided.

---

## 10. Decision Payload Example

A single decision option, serialized as it would be stored / returned by the API. This corresponds to the **SaaS A** row from the [worked example](#7-worked-example-three-ideas):

```json
{
  "decision_id": "dec_01HX9F3K2A",
  "company_id": "co_42",
  "decision_type": "idea",
  "status": "decided",
  "ai_recommendation": "Strong candidate",
  "overall_call": "Build now",
  "options": [
    {
      "option_id": "opt_saas_a",
      "option_type": "Idea",
      "option_name": "SaaS A",
      "scores": {
        "risk": 35,
        "complexity": 60,
        "potential": 82
      },
      "time_to_impact": "3-6 months",
      "capital_required": "$3k-$5k",
      "advisor_scores": {
        "yc_pmf": 80,
        "tech_feasibility": 90,
        "moonshot_potential": 55,
        "global_scale_ease": 85,
        "monetization_strength": 80
      },
      "advisor_recommendations": {
        "yc_accelerator": "Proceed",
        "deep_tech_validation": "Proceed",
        "moonshot_strategy": "Proceed with constraints",
        "global_ecosystem_builder": "Proceed",
        "fintech_product_excellence": "Proceed"
      },
      "justification": "Best balance of high potential (82) and moderate risk (35); strong PMF signal, high feasibility, strong monetization, easy to scale globally.",
      "chosen": true
    }
  ],
  "chosen_option_id": "opt_saas_a",
  "human_reasoning": "Aligns with my SaaS background; cash-flowing and exit-ready by design.",
  "decided_by": "founder",
  "decided_at": "2026-06-23T10:15:00Z",
  "activity_log_id": "log_01HX9F3M77"
}
```
