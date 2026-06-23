# Glossary

Definitions of the key terms and concepts used throughout MyUNO Capital and its documentation. See also the [Documentation home](index.md), the [Agents reference](agents.md), and the [Decision Hub guide](decision-hub.md).

---

### Agent

A specialized AI worker that performs a defined role within your virtual team — for example `IdeaValidationAgent`, `DevAgent`, or `ExitPlanningAgent`. Agents reason over tasks, call tools (HTTP, database, repos, third-party APIs), produce outputs, and emit events to the [Activity Log](#global-activity-log). They operate under the limits set by your [Autonomy Profile](#autonomy-profile) and are coordinated by the [Orchestrator](#orchestrator). See the full [Agents reference](agents.md).

### Advisor Agent

A special class of agent in the **Elite Advisor & Accelerator Layer** that encodes proven playbooks (YC-style accelerators, Tinkoff-like fintech/product excellence, MIT-like deep tech validation, Elon-like moonshot thinking, Jack Ma-like global ecosystem building). For major decisions, each advisor contributes a numeric score (0–100) for its dimension, a short narrative justification, and a recommendation (Proceed / Proceed with constraints / Park / Kill). Advisor agents encode analogous frameworks; they are not the individuals themselves.

### Founder Console

Your "cockpit" — the single web interface where you manage multiple businesses, set goals and limits, approve important actions, view dashboards (revenue, costs, profit, signups, churn, NPS, exit-readiness), and pause, adjust, or override the system at any time.

### Decision Hub

A central place to compare options and make decisions with data rather than gut feeling. Every major decision (ideas, features, channels, pricing, tech stacks) is represented as a set of options, each scored on Risk, Complexity, and Potential, plus Time to Impact and Capital Required, along with advisor scores and an AI recommendation. You make the final choice, which is logged with its reasoning. See [decision-hub.md](decision-hub.md).

### Autonomy Profile

The configurable policy that controls how much the platform can do without your approval. Three levels:

- **Ask me first** — everything requires approval.
- **Guided autonomy** — small decisions are automatic; big ones require approval.
- **Autonomous within limits** — fully automatic within budgets and guardrails.

Profiles support guardrails such as "Ask before spending > $100/day on ads" or "Require approval for production code deploys."

### Risk Score

A 0–100 score for an option where higher means more risky. Computed approximately as:

```text
Risk Score ≈ 0.30 × CompetitionIntensity
           + 0.25 × RegulatoryRisk
           + 0.25 × CapitalRequirement
           + 0.20 × PlatformDependence
```

All inputs are normalized to 0–100 internally. See [decision-hub.md](decision-hub.md).

### Complexity Score

A 0–100 score for an option where higher means more complex to execute. Computed approximately as:

```text
Complexity Score ≈ 0.40 × TechnicalComplexity
                 + 0.30 × ExecutionComplexity
                 + 0.30 × (IntegrationCount / NormalizationFactor)
```

### Potential Score

A 0–100 score for an option where higher means more upside. Computed approximately as:

```text
Potential Score ≈ 0.30 × MarketSize
                + 0.20 × TrendDirection
                + 0.20 × PricingPower
                + 0.15 × Scalability
                + 0.15 × FounderFit
```

### Time to Impact

A Decision Hub dimension estimating how long until an option produces its first meaningful result (e.g., "1–2 months", "3–6 months").

### Capital Required

A Decision Hub dimension estimating the rough cost to reach the first milestones for an option (e.g., "$500–$1k", "$10k+").

### Exit Readiness Score

A 0–100 score maintained by the `ExitPlanningAgent` that summarizes how prepared a business is for sale or M&A, based on financials, metrics, documentation, and operational stability. A target of **≥75/100** is used as a stage-gate for the ExitPrep stage.

### Tenant

An isolated account boundary within the multi-tenant platform. Each tenant's data is logically isolated in the database (per-tenant schemas/keys) with strict access control in the application layer. A tenant can contain multiple companies/projects.

### Company (Project)

A single business managed inside a tenant, with its own goals, agents, integrations, KPIs, options, and decisions. The platform is deliberately multi-business so a solo founder can run several companies in parallel.

### Orchestrator

The AI coordination layer that routes tasks to the appropriate models and agents, sequences multi-agent workflows, schedules background work, and exposes tool calling. It is **provider-agnostic**, defaulting to Anthropic Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`) with model routing by task type.

### Playbook

A reusable, structured set of steps, checklists, and best practices an agent follows to accomplish a goal (e.g., a YC-style 4–8 week growth sprint, or a validation experiment plan). Business model templates ship with default agents and playbooks.

### Stage

A phase in the idea→exit lifecycle. The stage map runs: **0. Ideation → 1. Validate → 2. Build → 3. Launch → 4. Grow → 5. Scale → 6. ExitPrep → 7. Exit**. Each stage has key outputs, success criteria, pivot triggers, and advisor checkpoints. See [roadmap.md](roadmap.md).

### Pivot Trigger

A predefined condition that signals it may be time to change direction within or between stages — for example "all ideas Potential <60 or Risk >70" at Ideation, or "CAC too high vs LTV" at Grow. When a pivot trigger fires, agents recommend proceed / pivot / kill.

### MRR (Monthly Recurring Revenue)

The predictable subscription revenue a business earns each month. A primary growth KPI tracked by the `DataAgent` and `FinanceAgent`.

### CAC (Customer Acquisition Cost)

The average cost to acquire one paying customer. Monitored against [LTV](#ltv-lifetime-value) to ensure healthy unit economics (target LTV ≥ 3× CAC).

### LTV (Lifetime Value)

The total expected revenue from a customer over their lifetime. Used with [CAC](#cac-customer-acquisition-cost) and payback period to assess unit economics.

### Churn

The rate at which customers cancel or stop paying over a period. A core retention KPI; high churn is a common pivot trigger.

### Data Room

A structured, organized collection of financials, metrics, documentation, and legal materials prepared for due diligence during an exit. The `ExitPlanningAgent` produces data room outlines and supporting documents.

### Activity Log

See [Global Activity Log](#global-activity-log).

### Global Activity Log

A record of every significant agent and human action across the platform. It underpins trust, debugging, compliance, and exit due diligence, and complements short-term task memory and company-level memory.

### Validation Report

The output of a validation experiment produced by the `IdeaValidationAgent`: market and competition research, experiment results, computed Risk/Complexity/Potential scores, and an AI recommendation (proceed / pivot / kill).

### Guardrail

A hard limit or rule that constrains agent behavior regardless of autonomy level — e.g., spend caps, required approvals for production deploys or payment changes, and sandboxed testing before risky actions.

### Multi-Tenancy

The architectural property that lets many isolated tenants share the same platform safely, via logical DB isolation and strict per-tenant access control. See [architecture.md](architecture.md).

### pgvector

The PostgreSQL extension used to store and query vector embeddings for semantic memory, enabling agents to recall relevant company knowledge and prior decisions.
