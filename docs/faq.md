# Frequently Asked Questions

Practical answers about MyUNO Capital. For definitions, see the [Glossary](glossary.md); for setup, see [Getting Started](getting-started.md); to go deeper on the AI, see [Agents](agents.md) and the [Decision Hub](decision-hub.md).

---

### 1. What is MyUNO Capital?

MyUNO Capital is an **Autonomous AI Operating System for solo entrepreneurs**. It gives one person a full-stack virtual team — strategy, product, engineering, marketing, sales, support, finance, legal-lite, and exit planning — so you can run one or several businesses end-to-end, from first idea to a successful exit. You manage everything from a single [Founder Console](glossary.md#founder-console), set goals and guardrails, and approve key actions.

### 2. Who is it for?

Solo entrepreneurs and indie hackers, digital nomads and expat founders (e.g., Phuket, Bali, Chiang Mai), freelancers and consultants productizing their skills, and side-project builders turning projects into businesses. Secondary users include venture studios and small agencies running many solo-led experiments or micro-products.

### 3. Does the AI act on its own? How do I stay in control?

You set an [Autonomy Profile](glossary.md#autonomy-profile) per business with three levels: **Ask me first** (everything needs approval), **Guided autonomy** (small decisions auto, big ones need approval), and **Autonomous within limits** (fully automatic within budgets and guardrails). You can add guardrails like "Ask before spending > $100/day on ads" or "Require approval for production deploys", and you can pause, adjust, or override at any time. Defaults are conservative, and we recommend starting in copilot/assistant mode and increasing autonomy gradually.

### 4. How does it keep agents from doing something harmful?

Several layers: conservative autonomy defaults, required approvals for high-risk actions, sandboxed tests before risky changes, automatic rollbacks on failure (e.g., the `DevOpsAgent` rolls back failed deploys), and a [Global Activity Log](glossary.md#global-activity-log) recording every significant agent and human action for trust, debugging, and audit.

### 5. What happens to my data and my customers' data?

Customer data is **not** used to train shared models unless you explicitly opt in. Each [tenant](glossary.md#tenant) is logically isolated, with strict per-tenant access control, encrypted storage for secrets and sensitive data, and HTTPS/TLS for all traffic. You get data export and deletion mechanisms per tenant. The platform is designed GDPR-aware, with DPAs available for customers. See [Security & Compliance](security-compliance.md).

### 6. What are the pricing tiers?

| Tier | Price | Companies | Tasks/Month | Highlights |
|------|-------|-----------|-------------|------------|
| **Free** | $0 / month | 1 | ~50 | Basic idea validation, console access, manual approval only |
| **Solo Starter** | ~$49 / month | 2 | ~500 | Core agents (IdeaValidation, Strategy, Dev, Support, Finance) |
| **Solo Pro** | ~$149 / month | Unlimited | 5,000+ | Full agent suite incl. funding & exit agents, priority support, advanced dashboards |
| **Studio / Incubator** | Custom ($499+) | Bulk | Custom | White-label, custom templates, dedicated support |

Add-ons include usage-based task/agent-hour bundles, premium AI model usage, custom agent tuning, and an optional **exit success fee** model (lower base fee plus a small, capped % of exit value — only when the platform clearly facilitated the exit).

### 7. Which integrations are supported?

Out of the box and on the roadmap: **Development & Product** (GitHub/GitLab, Jira/Linear, Notion/Confluence); **Deployment** (Vercel/Netlify/Render, AWS/GCP/Azure); **Payments** (Stripe at MVP; later PayPal, Paddle, Shopify, WooCommerce); **CRM & Sales** (HubSpot/Pipedrive, plus a simple built-in CRM); **Marketing & Ads** (Google Ads, Meta Ads; later LinkedIn, TikTok); **Email & Comms** (Gmail/Outlook, SendGrid/Mailgun/Postmark, Slack/Teams); **Support** (Intercom/Zendesk/Help Scout); and **Analytics** (Google Analytics, event tracking, optional Postgres/BigQuery warehouse). See [Integrations](integrations.md).

### 8. Can I run it self-hosted?

Yes. The platform ships as a containerized stack you can run locally or in your own infrastructure. Local development uses Docker Compose (frontend, backend, PostgreSQL 16 + pgvector, Redis 7, MinIO for S3-compatible storage); production runs on Kubernetes. You bring your own LLM provider API key. See [Getting Started](getting-started.md) and [Deployment](deployment.md). Note that some managed integrations and higher-tier features (e.g., SSO) depend on your configuration.

### 9. Which LLM does it use?

The platform uses a **provider-agnostic orchestrator**, defaulting to **Anthropic Claude**. Three models are used and routed by task type: `claude-haiku-4-5` for light, fast tasks; `claude-sonnet-4-6` for standard reasoning; and `claude-opus-4-8` for complex, multi-step reasoning. Because the orchestrator is provider-agnostic, other LLM providers can be configured. Model routing and caching help keep cost and latency in check.

### 10. How does the Decision Hub scoring work?

For every major decision, options are scored on three 0–100 dimensions and two practical estimates:

- **Risk** (higher = riskier): competition intensity, regulatory risk, capital requirement, platform dependence.
- **Complexity** (higher = harder): technical complexity, execution complexity, integration count.
- **Potential** (higher = more upside): market size, trend direction, pricing power, scalability, founder fit.
- **Time to Impact** and **Capital Required** as practical estimates.

[Advisor agents](glossary.md#advisor-agent) add their own 0–100 dimension scores (e.g., YC PMF, tech feasibility, monetization strength) with narrative justifications and a recommendation (Proceed / Proceed with constraints / Park / Kill). The Hub shows all scores and an AI recommendation; **you make the final choice**, and the decision plus reasoning is logged. Full formulas are in [Decision Hub](decision-hub.md).

### 11. How does exit planning work?

The `ExitPlanningAgent` maintains an [Exit Readiness Score](glossary.md#exit-readiness-score) (0–100) based on financials, metrics, documentation, and operational stability, and prepares [Data Room](glossary.md#data-room) outlines and due diligence documents. When you reach the ExitPrep stage (target readiness ≥75/100), the `AcquirerOutreachAgent` identifies likely acquirers (strategic buyers, aggregators, individuals) and drafts outreach you approve. If selling isn't the right path, the `WindDownAgent` orchestrates a graceful shutdown — customer communication, offboarding, and optional asset sale (domain, code, audience).

### 12. Can I run multiple businesses at once?

Yes — that's a core design goal. Each business is a separate [company/project](glossary.md#company-project) inside your [tenant](glossary.md#tenant), with its own goals, agents, integrations, and KPIs. The intent is to run multiple ideas in parallel, kill weak ones early using stage-based pivot triggers, double down on winners, and keep each business exit-ready by design.

### 13. What is the Elite Advisor & Accelerator Layer?

It is a set of advisor agents that encode proven frameworks: a **YC Accelerator Agent** (PMF diagnostics, growth sprints, investor narratives), a **Fintech/Product Excellence Agent** (pricing, unit economics, reliability for anything money-related), a **Deep Tech Validation Agent** (technical feasibility, prior art, low-cost experiments), a **Moonshot Strategy Agent** (10x goals, first-principles decomposition, tail-risk analysis), and a **Global Ecosystem Builder Agent** (market scoring, partnerships, localization, scale strategy). They contribute scores and recommendations to the Decision Hub. See [Agents](agents.md).

### 14. How do the lifecycle stages and pivots work?

Each business moves through stages — **Ideation → Validate → Build → Launch → Grow → Scale → ExitPrep → Exit** — with defined key outputs, success criteria, [pivot triggers](glossary.md#pivot-trigger), and advisor checkpoints. For example, Validation succeeds with enough signups/pre-orders and conversion, and triggers a pivot on weak signal after sufficient traffic. This keeps progress structured and makes "proceed / pivot / kill" decisions data-driven. See [Roadmap](roadmap.md).

### 15. I'm not technical — can I still use it?

Yes. Onboarding is guided and **no-code-first**: business model templates (B2B SaaS micro-product, niche e-commerce, productized service, info products, consulting/coaching) come with recommended integrations, pre-defined KPIs, default agents, and playbooks. The platform proposes code-based solutions only when needed, and higher tiers include human support for critical steps.

---

Have a question that isn't answered here? Open an issue (see [Contributing](../CONTRIBUTING.md)) or check the [Glossary](glossary.md).
