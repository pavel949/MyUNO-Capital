# MyUNO Capital — Product Roadmap & Lifecycle

This document covers two related roadmaps:

1. **The founder's journey** — the Stage Map every business moves through (Stage 0 Ideation → Stage 7 Exit).
2. **The platform's build roadmap** — the phased plan for building MyUNO Capital itself.

See also the [Product Overview](./overview.md), [API Reference](./api-reference.md), [Security & Compliance](./security-compliance.md), and [Decision Hub](./decision-hub.md).

---

## 1. The Stage Map (Idea → Exit)

Every business in MyUNO Capital advances through eight stages. Each stage has a focus, expected outputs, success criteria, pivot triggers, and advisor checkpoints (from the [elite advisor layer](#3-scoring-formulas-reference)).

| Stage | Focus | Key Outputs | Success Criteria (examples) | Pivot Triggers (examples) | Advisor Checkpoints |
|-------|-------|-------------|------------------------------|----------------------------|---------------------|
| **0. Ideation** | Generate & rank ideas | Ranked idea list, scores, short writeups | ≥5–10 ideas; ≥1 with Potential ≥70 & Risk ≤60 | All ideas Potential <60 or Risk >70 | Deep Tech, Moonshot |
| **1. Validate** | Prove demand cheaply | Landing page, experiments, validation report | ≥X signups/pre-orders; ≥Y% conversion | <X/2 signups after Z visitors; negative qualitative feedback | YC, Fintech |
| **2. Build** | Create MVP | Working product, payments, basic analytics | MVP shipped in ≤N weeks; first live users | >150% of planned build time; major blocks | Deep Tech |
| **3. Launch** | Get first paying customers | Public release, first revenue | 1–5 paying customers in defined window; strong feedback loop | Engaged users but no payers; poor engagement | YC, Global |
| **4. Grow** | Make revenue repeatable | Acquisition engines, retention, unit economics | Reach $X MRR; churn <Y%; LTV ≥3× CAC | CAC too high vs LTV; flat growth | YC, Fintech |
| **5. Scale** | Systematize & improve margins | Automations, SOPs, higher margins | Stable $X–$Y MRR; margin ≥Z%; documented processes | Growth plateau; intense competition | Global, YC |
| **6. ExitPrep** | Package for sale/M&A | Data room, exit score, acquirer list | Exit readiness ≥75/100; multiple interested buyers | No buyer interest after X months | YC, Global, Fintech |
| **7. Exit** | Sell or wind down | Signed deal OR clean shutdown | Closed transaction OR completed wind-down | Repeated deal failures | All advisors |

> **Advisor key:** *YC* = YC Accelerator Agent · *Fintech* = Fintech/Product Excellence Agent (Tinkoff-like) · *Deep Tech* = Deep Tech Validation Agent (MIT-like) · *Moonshot* = Moonshot Strategy Agent (Elon-like) · *Global* = Global Ecosystem Builder Agent (Jack Ma–like).

---

## 2. Stage Checklists (Example: Stage 1 — Validation)

Each stage ships with a checklist. Here is the Validation stage as an example.

**Required:**

- [ ] Clear problem statement.
- [ ] Defined target persona(s).
- [ ] Landing/offer page live.
- [ ] At least one acquisition channel active (ads or outreach).
- [ ] Minimum traffic (e.g., 200–500 unique visitors).
- [ ] Conversion and engagement metrics logged.
- [ ] Validation report with AI recommendation: **proceed / pivot / kill**.

**Optional (Accelerators):**

- [ ] 3–10 user interviews with notes.
- [ ] Pre-orders or paid waitlist.
- [ ] Competitor comparison matrix.

---

## 3. Scoring Formulas Reference

Major decisions are scored in the **[Decision Hub](./decision-hub.md)**, which is the authoritative source for the formulas and advisor scoring. In brief, every option carries three core scores (all normalized to **0–100**):

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

On top of these, each elite advisor contributes a **numeric score (0–100)**, a short narrative justification, and a recommendation (Proceed / Proceed with constraints / Park / Kill). See the [Decision Hub](./decision-hub.md) for the full treatment.

---

## 4. Platform Build Roadmap (Phased Milestones)

This is the roadmap for building MyUNO Capital itself, derived from the founder's next steps. The strategy is to ship a working **core loop** first, then layer dashboards, growth/exit agents, multi-tenant scale, and compliance.

| Phase | Goal | Key Deliverables |
|-------|------|------------------|
| **Phase 1 — Core Loop** | Take a founder from **idea → MVP → first signups** in a single, working flow. | **IdeaValidationAgent** (research, experiments, Risk/Complexity/Potential scores, validation report) → **ProductManagerAgent + DevAgent** (specs, code in repo with branching/PRs, payments/auth/analytics) → **MarketingStrategyAgent + AdsAgent** (channels, campaigns within budget guardrails). Founder Console basics, goals/OKRs, autonomy profiles, approval checkpoints, JWT auth. |
| **Phase 2 — Dashboards & Decision Hub** | Give founders **data-driven visibility and decisions**. | Dashboards (MRR, churn, CAC, LTV, funnel, mission/task status); the **Decision Hub** with scored options, advisor scores, and justifications; activity log surfaced in the console; metrics aggregation. |
| **Phase 3 — Growth & Exit Agents** | Extend the team across **the full lifecycle**. | Growth agents (ContentAgent, SEOAgent, SalesAgent, SuccessAgent, SupportAgent, OpsAgent, DataAgent, AutomationAgent); funding & exit agents (**FundingReadinessAgent, ExitPlanningAgent** with exit-readiness score, **AcquirerOutreachAgent, WindDownAgent**); FinanceAgent and Legal/ComplianceAgent. |
| **Phase 4 — Multi-Tenant Scale & Advisor Layer** | Serve **tens of thousands** of solo founders, with elite guidance. | Hardened multi-tenant isolation, horizontal worker scaling, queue-based task handling, region-aware deployments/CDN; the full **Elite Advisor & Accelerator Layer** (YC / Fintech / Deep Tech / Moonshot / Global) wired into the Decision Hub; templates and guided onboarding at scale. |
| **Phase 5 — Compliance & SOC 2** | Earn **enterprise and studio trust**. | SOC 2 Type I then Type II; ISO 27001 readiness; SSO (SAML/OIDC), advanced RBAC, DPAs; formalized data export/deletion and audit tooling. See [Security & Compliance](./security-compliance.md). |

Throughout: the founder uses the platform on their own business first (dogfooding), then onboards 3–10 pilot solo founders, and continually refines and hardens the most valuable workflows.

---

## 5. Pricing Tiers (Reference)

| Tier | Price | Companies | Tasks/Month | Features |
|------|-------|-----------|-------------|----------|
| **Free** | $0 / month | 1 | ~50 | Basic idea validation, console access, manual approval only |
| **Solo Starter** | ~$49 / month | 2 | ~500 | Core agents (IdeaValidation, Strategy, Dev, Support, Finance) |
| **Solo Pro** | ~$149 / month | Unlimited | 5,000+ | Full agent suite including funding & exit agents, priority support, advanced dashboards |
| **Studio / Incubator** | Custom ($499+) | Bulk | Custom | White-label, custom templates, dedicated support |

**Add-ons:** extra task/agent-hour bundles (usage-based), premium AI model usage (pass-through or small markup), custom agent tuning on proprietary data, and an optional **exit success fee** (lower base fee + small capped % of exit value, only if the platform clearly facilitated the exit).

---

## Related Documentation

- [Product Overview](./overview.md)
- [API Reference](./api-reference.md)
- [Security & Compliance](./security-compliance.md)
- [Decision Hub](./decision-hub.md)

---

*© 2026 MyUNO Capital. All rights reserved.*
