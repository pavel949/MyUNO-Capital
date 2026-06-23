# Agents Reference — MyUNO Capital

> The complete reference for every agent in the MyUNO Capital Autonomous AI Operating System.

**Related docs:** [Decision Hub](./decision-hub.md) · [Project overview](../project.md)

---

## 1. What is an Agent in MyUNO Capital?

An **agent** is an autonomous, role-specialized AI worker that fills a specific seat on the founder's "virtual team." Where a traditional company would hire a strategist, a developer, a marketer, or a finance person, MyUNO Capital composes those roles as software agents that perceive the state of a business, plan their work, act through tools, and report back to the founder.

Each agent is:

- **Role-scoped** — it owns one functional domain (e.g., engineering, growth, finance) and the playbooks, prompts, and tools that go with it.
- **Tool-using** — it acts on the real world through tool calling: HTTP requests, database access, the file system, code repositories, and third-party APIs (Stripe, Google Ads, GitHub, etc.).
- **Memory-aware** — it reads and writes both short-term task memory (the current multi-step workflow) and company-level memory (goals, brand voice, prior decisions, domain knowledge), backed by a pgvector semantic store.
- **Governed** — every action it takes is gated by the founder's configured **autonomy profile** and logged to the global activity log.

Agents do not act in isolation. The **AI Orchestrator** routes tasks to the right agent(s), coordinates multi-agent workflows, and selects the appropriate LLM tier for each step.

---

## 2. Agent Lifecycle

Every agent run follows the same five-phase loop:

```text
┌───────────┐   ┌────────┐   ┌──────────────┐   ┌──────────┐   ┌─────────┐
│  Perceive │ → │  Plan  │ → │ Act via Tools │ → │ Reflect  │ → │ Report  │
└───────────┘   └────────┘   └──────────────┘   └──────────┘   └─────────┘
      ▲                                                              │
      └──────────────────── re-perceive on new input ───────────────┘
```

1. **Perceive** — The agent gathers context: the triggering task, relevant company-level memory, short-term task memory, current metrics, integration state, and the founder's goals and constraints.
2. **Plan** — Using its role playbook and an LLM appropriate to the task, the agent decomposes the goal into a sequence of steps, identifying which tools and which (if any) other agents are needed.
3. **Act via Tools** — The agent executes steps by calling tools (HTTP, DB, filesystem, repos, third-party APIs). Each tool call that exceeds the founder's autonomy thresholds pauses for approval.
4. **Reflect** — The agent evaluates results against the plan: did the experiment succeed, did the tests pass, did the deploy go green? It retries, adjusts, or escalates as needed.
5. **Report** — The agent writes artifacts (reports, code, copy, dashboards), updates memory, emits an entry to the global activity log, and surfaces results and recommendations in the Founder Console.

---

## 3. Composing the Virtual Team

A "company" in MyUNO Capital is a tenant with its own goals, integrations, KPIs, and an assembled roster of agents. Agents are composed into a team in three ways:

- **By template** — Business-model templates (B2B SaaS micro-product, niche e-commerce, productized service, info products, consulting) ship with a default set of agents and playbooks.
- **By lifecycle stage** — The orchestrator activates and prioritizes agents based on the current stage (Ideation → Validate → Build → Launch → Grow → Scale → ExitPrep → Exit).
- **By workflow** — Agents collaborate in end-to-end flows. The first core loop, for example, chains:

  ```text
  IdeaValidationAgent → ProductManagerAgent + DevAgent → MarketingStrategyAgent + AdsAgent
  ```

The **Elite Advisor & Accelerator Layer** sits above the functional agents, contributing multi-angle scoring and recommendations to the [Decision Hub](./decision-hub.md) at major decision points.

---

## 4. Autonomy Profiles & Action Gating

Every agent action is gated by the founder's configured autonomy profile. Profiles set the default posture; per-action guardrails (budgets, environments, payment changes) refine it.

| Autonomy Profile | Behavior | Typical use |
|------------------|----------|-------------|
| **Ask me first** | Everything requires explicit founder approval before execution. | New users, copilot mode, high-stakes businesses. |
| **Guided autonomy** | Small/reversible decisions run automatically; big or risky ones require approval. | Most active founders once trust is established. |
| **Autonomous within limits** | Fully automatic *within* configured budgets and guardrails; only limit-breaching actions stop for approval. | Mature, well-instrumented businesses. |

Examples of guardrails that override the profile:

- "Ask before spending > $100/day on ads."
- "Require approval for production code deploys."
- "Never change payment or pricing configuration without approval."

Each agent below documents its **Autonomy & approval requirements** — i.e., which of its actions are considered high-risk and therefore require human approval regardless of profile defaults.

---

## 5. All Agents at a Glance

### Functional Team (Section 4.3)

| Category | Agent | One-line purpose |
|----------|-------|------------------|
| Strategy, Finance & Legal-Lite | [IdeaValidationAgent](#ideavalidationagent) | Research markets and run cheap experiments to score and validate ideas. |
| Strategy, Finance & Legal-Lite | [StrategyAgent](#strategyagent) | Turn goals into product/GTM strategy, OKRs, and roadmaps. |
| Strategy, Finance & Legal-Lite | [FinanceAgent](#financeagent) | Track revenue/costs/profit and forecast cash flow, runway, and valuation. |
| Strategy, Finance & Legal-Lite | [Legal/ComplianceAgent](#legalcomplianceagent) | Draft legal docs and track basic compliance, flagging items for human review. |
| Product & Engineering | [ProductManagerAgent](#productmanageragent) | Define personas, write specs, and prioritize the backlog by impact vs effort. |
| Product & Engineering | [ArchitectAgent](#architectagent) | Choose the tech stack and design architecture and data models. |
| Product & Engineering | [DevAgent](#devagent-full-stack) | Write, refactor, and test full-stack code via repo branches and PRs. |
| Product & Engineering | [QAAgent](#qaagent) | Create test plans, run regression suites, file reproducible bug reports. |
| Product & Engineering | [DevOpsAgent](#devopsagent) | Set up CI/CD, manage deploys, monitor uptime, and roll back on failure. |
| Growth, Marketing & Content | [MarketingStrategyAgent](#marketingstrategyagent) | Pick acquisition channels and plan campaigns and content calendars. |
| Growth, Marketing & Content | [AdsAgent](#adsagent) | Run and optimize ad campaigns within strict budgets and guardrails. |
| Growth, Marketing & Content | [ContentAgent](#contentagent) | Write landing pages, sales copy, emails, blog, and social in brand tone. |
| Growth, Marketing & Content | [SEOAgent](#seoagent) | Keyword research plus on-page and basic technical SEO improvements. |
| Sales, Customer Success & Support | [SalesAgent](#salesagent) | Build compliant lead lists, run cold outreach, and book calls. |
| Sales, Customer Success & Support | [SuccessAgent](#successagent) | Design onboarding, track customer health, drive retention and expansion. |
| Sales, Customer Success & Support | [SupportAgent](#supportagent) | Answer tickets from the knowledge base and escalate complex issues. |
| Operations, Data & Automation | [OpsAgent](#opsagent) | Set up recurring tasks/SOPs and handle admin work. |
| Operations, Data & Automation | [DataAgent](#dataagent) | Build dashboards and ensure data consistency across tools. |
| Operations, Data & Automation | [AutomationAgent](#automationagent) | Connect tools and automate repetitive manual work. |
| Funding & Exit | [FundingReadinessAgent](#fundingreadinessagent) | Prepare pitch deck, one-pager, financial model, and investor list. |
| Funding & Exit | [ExitPlanningAgent](#exitplanningagent) | Maintain exit readiness score and assemble due-diligence materials. |
| Funding & Exit | [AcquirerOutreachAgent](#acquireroutreachagent) | Identify likely acquirers and draft outreach (founder approves). |
| Funding & Exit | [WindDownAgent](#winddownagent) | Manage graceful shutdown, offboarding, and asset sale. |

### Elite Advisor & Accelerator Layer (Section 4.4)

| Agent | One-line purpose |
|-------|------------------|
| [YC Accelerator Agent](#yc-accelerator-agent) | PMF diagnostics, growth sprints, investor narratives, mock Q&A. |
| [Fintech/Product Excellence Agent](#fintechproduct-excellence-agent-tinkoff-like) | Pricing/monetization design and unit-economics rigor on anything money-related. |
| [Deep Tech Validation Agent](#deep-tech-validation-agent-mit-like) | Technical feasibility scoring, prior-art mapping, low-cost experiments. |
| [Moonshot Strategy Agent](#moonshot-strategy-agent-elon-like) | 10x framing, first-principles decomposition, backcasting, tail-risk analysis. |
| [Global Ecosystem Builder Agent](#global-ecosystem-builder-agent-jack-malike) | Market scoring, partnerships, localization, and scale strategy. |

---

## 6. Strategy, Finance & Legal-Lite

### IdeaValidationAgent

**Purpose** — Determine, as cheaply and quickly as possible, whether an idea has real demand, and produce the scores that feed the [Decision Hub](./decision-hub.md).

**Key responsibilities**
- Research market size, trends, and competitive intensity.
- Design and run validation experiments: landing pages, ads, cold outreach, pre-orders, waitlists.
- Compute **Risk, Complexity, and Potential** scores (see [Scoring Formulas](./decision-hub.md#4-scoring-formulas)).
- Produce a validation report with a proceed / pivot / kill recommendation.

**Inputs** — Raw idea description, target persona hypotheses, founder constraints (budget, time), market research data, experiment results.

**Outputs / artifacts** — Validation report, scored options (Risk/Complexity/Potential), landing-page briefs, experiment dashboards, recommendation.

**Tools / integrations** — Web research (HTTP), landing-page/site builders, Google Ads & Meta Ads, email/outreach, analytics (GA, event tracking), DB, semantic memory.

**Default LLM / model tier** — `claude-opus-4-8` for synthesis and scoring; `claude-sonnet-4-6` for routine research; `claude-haiku-4-5` for bulk data extraction.

**Autonomy & approval requirements** — Spinning up experiments that incur cost (ad spend, paid tools) requires approval per the ad-budget guardrail. Read-only research runs freely. Final score-driven kill/pivot recommendations are advisory; the founder decides in the Decision Hub.

**Example trigger / task** — "Validate 'AI bookkeeping for freelancers' in 7 days." → researches market, ships a landing page, runs a $50/day ad test, reports conversion and a Potential score.

---

### StrategyAgent

**Purpose** — Translate high-level founder goals into an executable strategy and keep it aligned with reality as data comes in.

**Key responsibilities**
- Turn goals (e.g., "$10k MRR in 12 months") into product and go-to-market strategies.
- Maintain OKRs, roadmaps, and weekly action plans.
- Recommend focus, double-down, or pivot based on performance data.

**Inputs** — Founder goals and constraints, validation reports, metrics (revenue, growth, retention), competitive context, advisor scores.

**Outputs / artifacts** — OKRs, roadmap, weekly plans, pivot/focus recommendations, strategy memos.

**Tools / integrations** — DB, metrics aggregation, project tools (Jira/Linear/Notion), semantic memory.

**Default LLM / model tier** — `claude-opus-4-8` (strategic reasoning).

**Autonomy & approval requirements** — Strategy and roadmap changes are proposals surfaced for founder confirmation. It does not unilaterally re-prioritize committed work without approval under *Ask me first* / *Guided autonomy*.

**Example trigger / task** — "Growth has been flat for 3 weeks." → analyzes funnel and retention, proposes a pivot from paid ads to content-led growth, updates OKRs on approval.

---

### FinanceAgent

**Purpose** — Give the founder a clear, continuously updated financial picture and proactive guidance on cash, runway, and unit economics.

**Key responsibilities**
- Track revenue, expenses, and profit.
- Forecast cash flow, runway, and basic valuation ranges.
- Monitor unit economics; suggest cost cuts or budget reallocations.

**Inputs** — Stripe/payment data, expense feeds, ad spend, subscription/MRR data, CAC/LTV inputs.

**Outputs / artifacts** — Financial dashboards, cash-flow forecasts, runway alerts, valuation ranges, budget recommendations.

**Tools / integrations** — Stripe, accounting/expense sources, DB, data warehouse (Postgres/BigQuery), DataAgent dashboards.

**Default LLM / model tier** — `claude-sonnet-4-6` for routine reporting; `claude-opus-4-8` for valuation and scenario modeling.

**Autonomy & approval requirements** — Read/report freely. Any action that *moves money* or changes payment/pricing configuration requires approval regardless of profile.

**Example trigger / task** — "How long is my runway?" → pulls Stripe + expenses, returns a 9-month runway with a forecast and two cost-cut options.

---

### Legal/ComplianceAgent

**Purpose** — Provide assistant-mode legal drafting and basic compliance tracking, while clearly flagging anything that needs a real lawyer.

**Key responsibilities**
- Draft ToS, privacy policy, NDAs, and simple contracts.
- Track basic compliance tasks (e.g., GDPR-related).
- Flag areas needing human legal review.

**Inputs** — Business model, jurisdictions, data-handling practices, integration list, contract requirements.

**Outputs / artifacts** — Draft legal documents, compliance checklists, GDPR/data-handling notes, "needs human review" flags.

**Tools / integrations** — Document storage (Drive), DB, semantic memory, web research for jurisdictional context.

**Default LLM / model tier** — `claude-opus-4-8` (careful drafting and risk flagging).

**Autonomy & approval requirements** — Operates strictly in assistant mode. Never represents output as legal advice; always recommends human counsel for material matters. Publishing legal docs to a live site requires approval.

**Example trigger / task** — "I need a privacy policy for an EU SaaS." → drafts a GDPR-aware policy, lists data flows, and flags cross-border transfer as needing legal review.

---

## 7. Product & Engineering

### ProductManagerAgent

**Purpose** — Own the "what and why" of the product: who it's for, what to build, and in what order.

**Key responsibilities**
- Define user personas and jobs-to-be-done.
- Write product specs, user stories, and acceptance criteria.
- Prioritize the backlog by impact vs effort.

**Inputs** — Strategy and OKRs, validation insights, customer feedback, support trends, usage analytics.

**Outputs / artifacts** — Personas, PRDs/specs, user stories with acceptance criteria, prioritized backlog.

**Tools / integrations** — Notion/Confluence, Jira/Linear, DB, analytics, semantic memory.

**Default LLM / model tier** — `claude-opus-4-8` (spec quality and prioritization).

**Autonomy & approval requirements** — Specs and backlog ordering are proposals; founder confirms scope before DevAgent builds. Low-risk grooming can run under *Guided autonomy*.

**Example trigger / task** — "Plan the MVP for the bookkeeping idea." → produces personas, a prioritized backlog, and acceptance criteria for the top 5 stories.

---

### ArchitectAgent

**Purpose** — Choose the right build approach and design a sound, maintainable system for the product.

**Key responsibilities**
- Choose the tech stack (no-code / low-code / full code), preferring no-code-first.
- Design architecture and data models.

**Inputs** — Product specs, scale and budget constraints, integration needs, non-functional requirements.

**Outputs / artifacts** — Architecture diagrams, tech-stack decision (with Decision Hub options), data-model schemas, integration plans.

**Tools / integrations** — Repos (GitHub/GitLab), DB, diagram/doc tools, semantic memory.

**Default LLM / model tier** — `claude-opus-4-8` (architecture reasoning).

**Autonomy & approval requirements** — Tech-stack choices are surfaced as scored options in the [Decision Hub](./decision-hub.md) for founder selection. No production infrastructure provisioned without approval.

**Example trigger / task** — "Pick a stack for the MVP." → proposes no-code (Bubble + Stripe) vs full-code (FastAPI + Next.js) as scored options with trade-offs.

---

### DevAgent (Full Stack)

**Purpose** — Implement the product: write, refactor, test, and document backend and frontend code in the founder's repository.

**Key responsibilities**
- Write and refactor backend and frontend code.
- Write tests and basic docs.
- Work in the repo with proper branching and PRs.

**Inputs** — Specs and acceptance criteria, architecture decisions, repo state, QA bug reports.

**Outputs / artifacts** — Feature branches, pull requests, code, tests, basic documentation.

**Tools / integrations** — GitHub/GitLab (branches, PRs), filesystem, CI, DB, semantic memory.

**Default LLM / model tier** — `claude-opus-4-8` for complex implementation/refactors; `claude-sonnet-4-6` for routine changes.

**Autonomy & approval requirements** — Opens branches and PRs freely. **Merging to main and production deploys require approval** (production-deploy guardrail). Never commits secrets.

**Example trigger / task** — "Implement Stripe checkout from the spec." → creates a branch, implements the flow, writes tests, and opens a PR for review.

---

### QAAgent

**Purpose** — Protect quality by systematically testing the product and reporting defects clearly.

**Key responsibilities**
- Create test plans and automated tests where possible.
- Run regression suites.
- File reproducible bug reports.

**Inputs** — Specs and acceptance criteria, new PRs/builds, prior test history.

**Outputs / artifacts** — Test plans, automated test suites, regression results, reproducible bug reports.

**Tools / integrations** — Repos, CI test runners, filesystem, issue tracker, DB.

**Default LLM / model tier** — `claude-sonnet-4-6`; `claude-haiku-4-5` for high-volume test generation.

**Autonomy & approval requirements** — Runs tests and files bugs autonomously. Does not modify product code (hands fixes to DevAgent).

**Example trigger / task** — "QA the checkout PR." → generates a test plan, runs the suite, and files a reproducible bug for a failed declined-card path.

---

### DevOpsAgent

**Purpose** — Keep the product shippable and running: pipelines, deployments, monitoring, and recovery.

**Key responsibilities**
- Set up CI/CD pipelines.
- Manage staging/production deployments.
- Monitor uptime and basic performance metrics.
- Roll back on failure and notify the founder.

**Inputs** — Repo and build artifacts, environment configs, health/metrics signals, deploy requests.

**Outputs / artifacts** — CI/CD pipelines, deployment records, uptime/performance dashboards, rollback events, incident notifications.

**Tools / integrations** — GitHub Actions/GitLab CI, Vercel/Netlify/Render, cloud (AWS/GCP/Azure), monitoring/observability, DB.

**Default LLM / model tier** — `claude-sonnet-4-6`; `claude-opus-4-8` for incident diagnosis.

**Autonomy & approval requirements** — **Production deploys require approval.** Automated rollback on failed deploys is permitted under *Guided autonomy* and *Autonomous within limits* (it always notifies the founder afterward). Staging deploys run freely.

**Example trigger / task** — "Deploy the approved checkout PR to production." → after approval, deploys, watches health checks, and rolls back automatically if error rate spikes.

---

## 8. Growth, Marketing & Content

### MarketingStrategyAgent

**Purpose** — Decide where and how to acquire customers, and orchestrate the marketing calendar.

**Key responsibilities**
- Select primary acquisition channels per business model.
- Plan multi-week campaigns and content calendars.

**Inputs** — Business model and persona, budget, prior channel performance, competitive landscape, strategy/OKRs.

**Outputs / artifacts** — Channel strategy, campaign plans, content calendars, channel options for the Decision Hub.

**Tools / integrations** — Analytics, ad platforms, CRM, content/CMS tools, DB, semantic memory.

**Default LLM / model tier** — `claude-opus-4-8` (channel strategy).

**Autonomy & approval requirements** — Plans are proposals. Activating paid channels triggers AdsAgent under the ad-budget guardrail (approval required above thresholds).

**Example trigger / task** — "Plan launch marketing for the SaaS." → recommends content + Google Ads, with a 6-week calendar and budget split as scored channel options.

---

### AdsAgent

**Purpose** — Execute and continuously optimize paid acquisition while respecting strict budget guardrails.

**Key responsibilities**
- Set up and manage ad campaigns (Google, Meta, etc.).
- Run A/B tests and optimize bids.
- Respect strict budgets and guardrails.

**Inputs** — Campaign plan, creative/copy from ContentAgent, budgets and guardrails, performance data.

**Outputs / artifacts** — Live campaigns, A/B test results, bid/budget optimizations, spend and ROAS reports.

**Tools / integrations** — Google Ads, Meta Ads (later LinkedIn/TikTok), analytics, DB.

**Default LLM / model tier** — `claude-sonnet-4-6`; `claude-haiku-4-5` for bulk creative variants.

**Autonomy & approval requirements** — Spend is hard-gated by the per-day/per-campaign budget guardrail (e.g., "ask before > $100/day"). Within limits and under *Autonomous within limits*, it optimizes bids automatically; budget increases always require approval.

**Example trigger / task** — "Run a $50/day validation campaign." → builds ad sets, A/B tests creatives, and reports CPC/conversion, never exceeding the cap without approval.

---

### ContentAgent

**Purpose** — Produce on-brand written content across the funnel.

**Key responsibilities**
- Write landing pages and sales copy.
- Write email sequences.
- Write blog posts and social content.
- Match the founder's brand tone.

**Inputs** — Brand voice (company memory), campaign briefs, personas, keywords from SEOAgent, product details.

**Outputs / artifacts** — Landing-page copy, sales copy, email sequences, blog posts, social posts.

**Tools / integrations** — CMS/site builders, email tools (SendGrid/Mailgun/Postmark), social tools, semantic memory (brand voice).

**Default LLM / model tier** — `claude-opus-4-8` for flagship copy; `claude-sonnet-4-6` / `claude-haiku-4-5` for volume.

**Autonomy & approval requirements** — Drafts freely. Publishing live to the website or sending to a real email list requires approval under *Ask me first* / *Guided autonomy*.

**Example trigger / task** — "Write the launch landing page." → produces a hero, benefits, social proof, and CTA copy in the saved brand tone.

---

### SEOAgent

**Purpose** — Grow organic visibility through keyword strategy and on-page/technical SEO.

**Key responsibilities**
- Perform keyword research.
- Suggest and implement on-page and basic technical SEO improvements.

**Inputs** — Site content and structure, target keywords, competitor SERP data, analytics.

**Outputs / artifacts** — Keyword lists, on-page recommendations, technical SEO fixes, content briefs for ContentAgent.

**Tools / integrations** — Search/keyword data (HTTP), CMS, site/repo for on-page changes, analytics, DB.

**Default LLM / model tier** — `claude-sonnet-4-6`.

**Autonomy & approval requirements** — Research and recommendations run freely. Live changes to production site content/markup require approval.

**Example trigger / task** — "Improve SEO for the blog." → returns a keyword cluster, meta/title fixes, and an internal-linking plan.

---

## 9. Sales, Customer Success & Support

### SalesAgent

**Purpose** — Generate pipeline through compliant outreach and book qualified calls.

**Key responsibilities**
- Build lead lists (within compliance rules).
- Send cold outreach sequences.
- Book calls into the founder's calendar.

**Inputs** — ICP/persona, compliance rules, outreach templates, CRM data, calendar availability.

**Outputs / artifacts** — Lead lists, outreach sequences, reply tracking, booked meetings.

**Tools / integrations** — Prospecting/enrichment, email (Gmail/Outlook, SendGrid), calendar, CRM (HubSpot/Pipedrive/built-in), DB.

**Default LLM / model tier** — `claude-sonnet-4-6`; `claude-haiku-4-5` for personalization at scale.

**Autonomy & approval requirements** — Must honor compliance rules (consent, opt-out, regional law). Sending cold outreach to real recipients requires approval under *Ask me first*; *Guided autonomy* permits sending within approved templates and caps. Calendar booking is permitted.

**Example trigger / task** — "Find 50 qualified leads and start outreach." → enriches a compliant list, sends a 3-step sequence (on approval), and books replies into the calendar.

---

### SuccessAgent

**Purpose** — Keep customers onboarded, healthy, and expanding.

**Key responsibilities**
- Design onboarding flows.
- Track customer health.
- Suggest retention and expansion actions.

**Inputs** — Usage/engagement data, churn signals, support history, plan/billing data.

**Outputs / artifacts** — Onboarding flows, health scores, churn-risk alerts, retention/expansion playbooks.

**Tools / integrations** — Product analytics, CRM, email, Stripe (plan data), DB, DataAgent dashboards.

**Default LLM / model tier** — `claude-sonnet-4-6`.

**Autonomy & approval requirements** — Health tracking and internal alerts run freely. Customer-facing messages and any upsell/discount offers require approval (or pre-approved templates under *Guided autonomy*).

**Example trigger / task** — "Reduce week-1 churn." → designs a 3-email onboarding flow and flags 5 at-risk accounts with recommended actions.

---

### SupportAgent

**Purpose** — Resolve customer support requests quickly and consistently, learning over time.

**Key responsibilities**
- Answer support tickets via email/chat using the knowledge base.
- Learn from resolved tickets.
- Escalate complex or sensitive issues.

**Inputs** — Incoming tickets, knowledge base, prior resolved tickets, account/billing context.

**Outputs / artifacts** — Ticket responses, updated KB articles, escalation tickets, resolution metrics.

**Tools / integrations** — Intercom/Zendesk/Help Scout, email, knowledge base + semantic memory, Stripe (billing lookups), DB.

**Default LLM / model tier** — `claude-haiku-4-5` for routine tickets; `claude-sonnet-4-6` for nuanced ones.

**Autonomy & approval requirements** — Can auto-respond to routine tickets under *Guided autonomy* / *Autonomous within limits*. Refunds, account changes, and sensitive/legal issues are escalated to the founder. Refund actions require approval (money-moving guardrail).

**Example trigger / task** — "Handle the support inbox." → answers FAQ-style tickets from the KB, escalates a billing dispute, and proposes a new KB article from a recurring question.

---

## 10. Operations, Data & Automation

### OpsAgent

**Purpose** — Run the recurring administrative backbone of the business.

**Key responsibilities**
- Set up recurring tasks and internal SOPs.
- Manage admin tasks (e.g., invoice reminders, monthly reports).

**Inputs** — Business calendar, billing/invoice data, recurring obligations, SOP templates.

**Outputs / artifacts** — SOP documents, scheduled tasks, invoice reminders, monthly operating reports.

**Tools / integrations** — Calendar, email, Stripe/invoicing, Notion/Drive, DB, scheduler (Celery/Redis-backed).

**Default LLM / model tier** — `claude-haiku-4-5` for routine ops; `claude-sonnet-4-6` for report synthesis.

**Autonomy & approval requirements** — Internal admin and reminders run freely. Sending invoice reminders to customers uses pre-approved templates; anything money-related requires approval.

**Example trigger / task** — "Send me a monthly business report." → compiles revenue, costs, and KPIs and schedules it for the 1st of each month.

---

### DataAgent

**Purpose** — Provide trustworthy metrics and dashboards across the business.

**Key responsibilities**
- Create dashboards (MRR, churn, CAC, LTV, funnel analytics).
- Ensure data consistency across tools.

**Inputs** — Source data from Stripe, analytics, CRM, ad platforms, product events.

**Outputs / artifacts** — Dashboards, metric definitions, data-quality/consistency reports.

**Tools / integrations** — Data warehouse (Postgres/BigQuery), analytics, Stripe, CRM, ad platforms, DB.

**Default LLM / model tier** — `claude-sonnet-4-6`.

**Autonomy & approval requirements** — Read and build dashboards freely. Schema/pipeline changes to founder-owned warehouses require approval.

**Example trigger / task** — "Build me a growth dashboard." → unifies Stripe + GA + CRM into one MRR/churn/CAC/LTV dashboard and flags a CAC mismatch between sources.

---

### AutomationAgent

**Purpose** — Eliminate repetitive manual work by connecting tools and building automations.

**Key responsibilities**
- Connect tools (Zapier-style automations).
- Identify repetitive manual work and propose automations.

**Inputs** — Tool inventory and APIs, observed manual workflows, activity-log patterns.

**Outputs / artifacts** — Automation workflows, integration connectors, automation proposals with ROI estimates.

**Tools / integrations** — Integration/connector layer (HTTP APIs), Zapier-style automations, DB, activity log.

**Default LLM / model tier** — `claude-sonnet-4-6`.

**Autonomy & approval requirements** — Proposing and testing automations in sandbox runs freely. Activating automations that touch live customer/payment data requires approval.

**Example trigger / task** — "Automate new-customer onboarding." → builds a flow: Stripe payment → CRM record → welcome email → onboarding task, tested in sandbox before activation.

---

## 11. Funding & Exit

### FundingReadinessAgent

**Purpose** *(optional agent)* — Prepare the founder to raise capital if they choose to.

**Key responsibilities**
- Prepare pitch deck, one-pager, and a simple financial model.
- Assemble a target investor list.

**Inputs** — Metrics and financials, strategy/vision, market data, traction evidence.

**Outputs / artifacts** — Pitch deck, one-pager, financial model, target investor list.

**Tools / integrations** — Drive/Canva (deck), FinanceAgent data, investor databases (HTTP), DB, semantic memory.

**Default LLM / model tier** — `claude-opus-4-8` (narrative and model quality).

**Autonomy & approval requirements** — Produces drafts only. Any outreach to investors requires founder approval. Coordinates with the YC Accelerator Agent for narrative and mock Q&A.

**Example trigger / task** — "Get me fundraising-ready." → builds a 12-slide deck, a one-pager, a 3-year model, and a 30-investor target list.

---

### ExitPlanningAgent

**Purpose** — Make the business exit-ready by design and quantify how ready it is.

**Key responsibilities**
- Maintain an **exit readiness score** based on financials, metrics, documentation, and operational stability.
- Prepare data-room outlines and due-diligence documentation.

**Inputs** — Financials, KPIs, documentation status, operational/process maturity, activity log.

**Outputs / artifacts** — Exit readiness score, data-room outline, due-diligence checklist and documents, gap analysis.

**Tools / integrations** — FinanceAgent + DataAgent outputs, Drive (data room), DB, activity log, semantic memory.

**Default LLM / model tier** — `claude-opus-4-8`.

**Autonomy & approval requirements** — Scoring and document prep run freely. Sharing a data room with external parties requires approval.

**Example trigger / task** — "How exit-ready am I?" → returns an exit readiness score of 68/100, a gap list (missing SOPs, churn too high), and a data-room outline.

---

### AcquirerOutreachAgent

**Purpose** — Find and approach likely buyers when the founder decides to sell.

**Key responsibilities**
- Identify likely acquirers (strategic buyers, aggregators, individuals).
- Draft outreach emails and follow-ups (founder approves).

**Inputs** — Business profile and metrics, exit readiness materials, acquirer landscape, founder's deal preferences.

**Outputs / artifacts** — Acquirer target list, outreach and follow-up drafts, response tracking.

**Tools / integrations** — Acquirer/marketplace databases (HTTP), email, CRM, DB, ExitPlanningAgent artifacts.

**Default LLM / model tier** — `claude-opus-4-8` (positioning) / `claude-sonnet-4-6` (drafting).

**Autonomy & approval requirements** — **All outbound acquirer communication requires founder approval**, explicitly per the spec ("you approve"). It drafts and queues but never sends autonomously.

**Example trigger / task** — "Find buyers for my SaaS." → builds a list of 15 strategic acquirers and aggregators with tailored outreach drafts awaiting approval.

---

### WindDownAgent

**Purpose** — Execute a clean, graceful shutdown when winding down is the right call.

**Key responsibilities**
- Manage graceful shutdown.
- Handle customer communication and offboarding.
- Manage asset sale (domain, code, audience) if desired.

**Inputs** — Decision to wind down, customer/subscription list, contractual obligations, asset inventory.

**Outputs / artifacts** — Shutdown plan and timeline, customer notices, offboarding/data-export flows, asset-sale listings.

**Tools / integrations** — Email, Stripe (cancellations/refunds), domain/asset marketplaces, Drive, DB, activity log.

**Default LLM / model tier** — `claude-sonnet-4-6`.

**Autonomy & approval requirements** — High-sensitivity. Customer notices, subscription cancellations, refunds, and asset sales all require explicit founder approval (money-moving + customer-facing guardrails).

**Example trigger / task** — "Wind down this product." → drafts a 30-day shutdown plan: customer notice, data export, final billing, and a listing to sell the domain and codebase.

---

## 12. Elite Advisor & Accelerator Layer (Section 4.4)

The Elite Advisor & Accelerator Layer encodes proven playbooks (YC-style accelerators, Tinkoff-level fintech/product operators, MIT-level deep tech labs, Elon Musk–style first-principles moonshot thinking, Jack Ma–style global ecosystem operators). These are abstractions of analogous frameworks — **not** the individuals themselves.

For major decisions (idea choice, market selection, funding vs bootstrapping, exit timing), each advisor contributes to the [Decision Hub](./decision-hub.md):

- A **numeric score (0–100)** for its dimension.
- A short narrative justification.
- A recommendation drawn from the taxonomy: **Proceed / Proceed with constraints / Park / Kill.**

These roll up into an **Overall Call** (e.g., *Build now* / *Park / R&D*). The founder still makes the final decision, now justified by multi-angle "elite" reasoning.

### YC Accelerator Agent

- **Dimension scored:** YC PMF Score (product-market fit, 0–100).
- **What it does:** PMF diagnostics using retention, engagement, and revenue data; designs 4–8 week growth sprints with KPIs; creates investor-ready narratives and deck outlines; runs mock investor Q&A.
- **Default model:** `claude-opus-4-8`.
- **Recommendation taxonomy:** Proceed / Proceed with constraints / Park / Kill.

### Fintech/Product Excellence Agent (Tinkoff-like)

- **Dimension scored:** Monetization Strength (0–100).
- **What it does:** Designs pricing and monetization models early; proposes pricing tiers and upsell ladders; monitors and improves unit economics (CAC, LTV, payback); enforces reliability standards on anything related to money.
- **Default model:** `claude-opus-4-8`.
- **Recommendation taxonomy:** Proceed / Proceed with constraints / Park / Kill.

### Deep Tech Validation Agent (MIT-like)

- **Dimension scored:** Tech Feasibility (0–100).
- **What it does:** Scores technical feasibility and risk; maps ideas to current state-of-the-art and prior art; proposes low-cost technical experiments; suggests high-level R&D roadmaps where needed.
- **Default model:** `claude-opus-4-8`.
- **Recommendation taxonomy:** Proceed / Proceed with constraints / Park / Kill.

### Moonshot Strategy Agent (Elon-like)

- **Dimension scored:** Moonshot Potential (0–100).
- **What it does:** Frames 10x goals and long-term visions; uses first-principles reasoning to decompose hard problems; designs backcasts from long-term outcomes to present-day steps; identifies existential / tail risks and mitigations.
- **Default model:** `claude-opus-4-8`.
- **Recommendation taxonomy:** Proceed / Proceed with constraints / Park / Kill.

### Global Ecosystem Builder Agent (Jack Ma–like)

- **Dimension scored:** Global Scale Ease (0–100).
- **What it does:** Scores markets by size, regulation, and ecosystem maturity; suggests partnerships and platform integrations; recommends localization (language, UX, pricing, payments); proposes scale strategies for B2B and B2C.
- **Default model:** `claude-opus-4-8`.
- **Recommendation taxonomy:** Proceed / Proceed with constraints / Park / Kill.

**Example advisor panel** (see the [Decision Hub worked example](./decision-hub.md#7-worked-example-three-ideas)):

| Option | YC PMF Score | Tech Feasibility | Moonshot Potential | Global Scale Ease | Monetization Strength | Overall Call |
|--------|--------------|------------------|--------------------|-------------------|------------------------|--------------|
| Idea A | 80/100       | High             | Medium             | High              | Strong                 | Build now    |
| Idea B | 40/100       | Medium           | Very High          | Medium            | Weak                   | Park / R&D   |

---

## 13. Adding a New Agent

All agents extend a common `BaseAgent` interface and are registered with the orchestrator's agent registry. The skeleton below uses the canonical stack (Python 3.12, async, provider-agnostic LLM orchestrator with model routing, tool calling, pgvector + company-level memory).

```python
# myuno/agents/base.py
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ModelTier(str, Enum):
    """Model routing tiers — mapped to concrete models by the LLM orchestrator."""
    COMPLEX = "claude-opus-4-8"    # complex reasoning
    MID = "claude-sonnet-4-6"      # mid-tier
    FAST = "claude-haiku-4-5"      # cheap / fast


class AutonomyProfile(str, Enum):
    ASK_FIRST = "ask_me_first"
    GUIDED = "guided_autonomy"
    AUTONOMOUS = "autonomous_within_limits"


@dataclass
class AgentContext:
    """Everything an agent needs to perceive its world."""
    company_id: str
    task: dict[str, Any]
    autonomy: AutonomyProfile
    guardrails: dict[str, Any] = field(default_factory=dict)  # e.g. {"ads_daily_usd": 100}


@dataclass
class AgentResult:
    summary: str
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    recommendation: str | None = None  # Proceed / Proceed with constraints / Park / Kill
    requires_approval: bool = False


class BaseAgent(abc.ABC):
    """Base interface for every MyUNO Capital agent.

    Lifecycle: perceive -> plan -> act (tools) -> reflect -> report.
    """

    name: str                       # e.g. "DevAgent"
    category: str                   # e.g. "Product & Engineering"
    default_tier: ModelTier = ModelTier.MID

    def __init__(self, llm, tools, memory):
        self.llm = llm        # provider-agnostic LLM orchestrator (model routing)
        self.tools = tools    # tool registry: http, db, filesystem, repos, 3rd-party APIs
        self.memory = memory  # pgvector semantic memory + company-level memory

    # --- lifecycle hooks (override as needed) -------------------------------

    async def perceive(self, ctx: AgentContext) -> dict[str, Any]:
        """Gather task context + relevant memory."""
        recall = await self.memory.search(ctx.company_id, query=ctx.task.get("goal", ""))
        return {"task": ctx.task, "memory": recall}

    @abc.abstractmethod
    async def run(self, ctx: AgentContext) -> AgentResult:
        """Main entry point invoked by the orchestrator.

        Implementations should:
          1. perceive()          -> gather context + memory
          2. plan with self.llm  -> route to a ModelTier
          3. act via self.tools  -> respecting ctx.autonomy / ctx.guardrails
          4. reflect             -> retry / adjust / escalate
          5. report              -> persist artifacts, write memory, log activity
        """
        ...

    async def needs_approval(self, ctx: AgentContext, action: dict[str, Any]) -> bool:
        """Default gate: high-risk or guardrail-breaching actions need a human."""
        if ctx.autonomy is AutonomyProfile.ASK_FIRST:
            return True
        return action.get("high_risk", False) or self._breaches_guardrail(ctx, action)

    def _breaches_guardrail(self, ctx: AgentContext, action: dict[str, Any]) -> bool:
        cap = ctx.guardrails.get("ads_daily_usd")
        return cap is not None and action.get("ads_daily_usd", 0) > cap
```

A concrete agent overrides `run` and declares its identity and default tier:

```python
# myuno/agents/seo_agent.py
from myuno.agents.base import BaseAgent, ModelTier, AgentContext, AgentResult


class SEOAgent(BaseAgent):
    name = "SEOAgent"
    category = "Growth, Marketing & Content"
    default_tier = ModelTier.MID

    async def run(self, ctx: AgentContext) -> AgentResult:
        perceived = await self.perceive(ctx)

        plan = await self.llm.complete(
            tier=self.default_tier,
            system="You are the SEOAgent. Do keyword research and on-page SEO.",
            input=perceived,
        )

        keywords = await self.tools.http.search_keywords(plan["seed_terms"])
        report = {"type": "seo_report", "keywords": keywords, "onpage": plan["fixes"]}

        await self.memory.write(ctx.company_id, kind="seo", data=report)
        return AgentResult(
            summary=f"Found {len(keywords)} keywords and {len(plan['fixes'])} on-page fixes.",
            artifacts=[report],
            recommendation="Proceed",
        )
```

Register it so the orchestrator can route tasks to it:

```python
# myuno/agents/registry.py
from myuno.agents.seo_agent import SEOAgent
from myuno.agents.dev_agent import DevAgent
# ... import other agents

AGENT_REGISTRY: dict[str, type] = {}


def register(agent_cls: type) -> type:
    """Decorator/function to add an agent to the global registry."""
    AGENT_REGISTRY[agent_cls.name] = agent_cls
    return agent_cls


# Register the built-in agents
for cls in (SEOAgent, DevAgent):  # ... add the rest
    register(cls)
```

**Checklist for adding a new agent:**

1. Create `myuno/agents/<your>_agent.py` subclassing `BaseAgent`; set `name`, `category`, and `default_tier`.
2. Implement `run()` following the perceive → plan → act → reflect → report lifecycle.
3. Declare the **tools/integrations** it needs and request them from the tool registry.
4. Define its **autonomy & approval rules** (override `needs_approval` if it has special high-risk actions).
5. If it participates in decisions, have it emit a 0–100 score + justification + recommendation for the [Decision Hub](./decision-hub.md).
6. `register(YourAgent)` in `registry.py`.
7. Add it to the relevant business-model templates and lifecycle-stage activation rules.
8. Document it in this file (purpose, responsibilities, inputs, outputs, tools, model tier, autonomy, example).
