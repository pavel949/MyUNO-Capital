"""Agent registry — maps every agent name to a class.

Implements real logic for IdeaValidationAgent, StrategyAgent, ProductManagerAgent,
and ContentAgent. The remaining roster is registered as configured GenericAgent
subclasses so the entire team is callable and produces a domain report.
"""

from __future__ import annotations

from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.services import scoring

# ---------------------------------------------------------------------------
# Registry plumbing
# ---------------------------------------------------------------------------
AGENT_REGISTRY: dict[str, type[BaseAgent]] = {}


def register(agent_cls: type[BaseAgent]) -> type[BaseAgent]:
    AGENT_REGISTRY[agent_cls.name] = agent_cls
    return agent_cls


def get_agent_class(name: str) -> type[BaseAgent] | None:
    return AGENT_REGISTRY.get(name)


# ---------------------------------------------------------------------------
# Helpers for normalizing/scoring idea inputs
# ---------------------------------------------------------------------------
def _norm(value: Any, default: float = 50.0) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return default
    return scoring.clamp(v)


# ---------------------------------------------------------------------------
# Concrete agents with real logic
# ---------------------------------------------------------------------------
@register
class IdeaValidationAgent(BaseAgent):
    key = "idea_validation"
    name = "IdeaValidationAgent"
    category = "strategy"
    description = (
        "Researches market, runs validation experiments, scores ideas "
        "(Risk/Complexity/Potential) and recommends proceed/pivot/kill."
    )
    default_model = "claude-opus-4-8"
    min_tier = "free"
    inputs_schema = ["idea", "target_persona", "budget", "factors"]
    high_risk_actions = ["launch_paid_experiment"]
    required_integrations = ["google_ads", "google_analytics"]

    def run(self, ctx: AgentContext) -> AgentResult:
        factors = ctx.inputs.get("factors", {}) if isinstance(ctx.inputs, dict) else {}

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

        llm = self.llm.complete(
            system=self.system_prompt(),
            prompt=self.build_prompt(ctx)
            + f"\nComputed scores -> risk={risk:.0f}, complexity={complexity:.0f}, "
            f"potential={potential:.0f}. Write a validation summary.",
            complexity="complex",
            context={"agent": self.name, "objective": ctx.objective},
        )

        summary = (
            f"Validation for '{ctx.objective}': potential {potential:.0f}, "
            f"risk {risk:.0f}, complexity {complexity:.0f}. Overall call: {rec.overall_call}."
        )
        return AgentResult(
            summary=summary,
            artifacts=[
                {
                    "type": "validation_report",
                    "scores": {
                        "risk": int(round(risk)),
                        "complexity": int(round(complexity)),
                        "potential": int(round(potential)),
                    },
                    "advisor_scores": advisor,
                    "overall_call": rec.overall_call,
                    "narrative": llm.text,
                }
            ],
            recommendation=rec.ai_recommendation,
            scores={
                "risk": int(round(risk)),
                "complexity": int(round(complexity)),
                "potential": int(round(potential)),
                "advisor_scores": advisor,
                "overall_call": rec.overall_call,
                "rationale": rec.rationale,
            },
            model_used=llm.model,
            token_input=llm.token_input,
            token_output=llm.token_output,
        )


@register
class StrategyAgent(BaseAgent):
    key = "strategy"
    name = "StrategyAgent"
    category = "strategy"
    description = "Turns goals into product/GTM strategy, OKRs, and roadmaps."
    default_model = "claude-opus-4-8"
    min_tier = "free"
    inputs_schema = ["goal", "horizon", "metrics"]

    def generate_okrs(self, ctx: AgentContext) -> list[dict[str, Any]]:
        """Produce OKRs from a goal. Used by the goals API."""
        goal_title = ctx.inputs.get("goal_title") or ctx.objective
        metric = ctx.inputs.get("metric") or "mrr"
        target = ctx.inputs.get("target_value") or 0
        self.llm.complete(
            system=self.system_prompt(),
            prompt=f"Generate quarterly OKRs for goal: {goal_title}.",
            complexity="complex",
            context={"agent": self.name, "objective": goal_title},
        )
        return [
            {
                "objective": "Validate demand and ship a payable MVP",
                "key_results": [
                    {"kr": "Land 200 unique landing-page visitors", "target": 200, "current": 0},
                    {"kr": "Reach 5% signup conversion", "target": 5, "current": 0},
                    {"kr": "Onboard 3 paying customers", "target": 3, "current": 0},
                ],
            },
            {
                "objective": f"Build a repeatable path toward the {metric} target",
                "key_results": [
                    {
                        "kr": f"Reach {round(float(target) * 0.3) if target else 30}% of target",
                        "target": round(float(target) * 0.3) if target else 30,
                        "current": 0,
                    },
                    {"kr": "Establish one reliable acquisition channel", "target": 1, "current": 0},
                ],
            },
        ]

    def run(self, ctx: AgentContext) -> AgentResult:
        okrs = self.generate_okrs(ctx)
        llm = self.llm.complete(
            system=self.system_prompt(),
            prompt=self.build_prompt(ctx),
            complexity="complex",
            context={"agent": self.name, "objective": ctx.objective},
        )
        return AgentResult(
            summary=f"Strategy and {len(okrs)} OKR objectives drafted for: {ctx.objective}.",
            artifacts=[{"type": "okrs", "objectives": okrs}, {"type": "memo", "text": llm.text}],
            recommendation="proceed",
            model_used=llm.model,
            token_input=llm.token_input,
            token_output=llm.token_output,
        )


@register
class ProductManagerAgent(BaseAgent):
    key = "product_manager"
    name = "ProductManagerAgent"
    category = "product_eng"
    description = "Defines personas, writes specs, and prioritizes the backlog by impact vs effort."
    default_model = "claude-opus-4-8"
    min_tier = "free"
    inputs_schema = ["strategy", "validation_insights", "feedback"]

    def run(self, ctx: AgentContext) -> AgentResult:
        llm = self.llm.complete(
            system=self.system_prompt(),
            prompt=self.build_prompt(ctx) + "\nProduce personas, top user stories, and a backlog.",
            complexity="complex",
            context={"agent": self.name, "objective": ctx.objective},
        )
        personas = [
            {"name": "Solo Consultant", "jtbd": "Stay on top of client work without overhead"},
            {"name": "Indie Maker", "jtbd": "Ship and monetize quickly with minimal ops"},
        ]
        backlog = [
            {"story": "As a user I can sign up and onboard in <2 min", "impact": 5, "effort": 2},
            {"story": "As a user I can connect my primary data source", "impact": 5, "effort": 3},
            {"story": "As a user I can see my core metric on a dashboard", "impact": 4, "effort": 2},
        ]
        return AgentResult(
            summary=f"PRD with {len(personas)} personas and {len(backlog)} backlog items drafted.",
            artifacts=[
                {"type": "personas", "items": personas},
                {"type": "backlog", "items": backlog},
                {"type": "prd", "text": llm.text},
            ],
            recommendation="proceed",
            requires_approval=ctx.autonomy.value == "ask_first",
            model_used=llm.model,
            token_input=llm.token_input,
            token_output=llm.token_output,
        )


@register
class ContentAgent(BaseAgent):
    key = "content"
    name = "ContentAgent"
    category = "growth"
    description = "Writes landing pages, sales copy, emails, blog, and social in brand tone."
    default_model = "claude-opus-4-8"
    min_tier = "free"
    inputs_schema = ["brand_voice", "brief", "personas", "keywords"]
    high_risk_actions = ["publish_live", "send_to_list"]

    def run(self, ctx: AgentContext) -> AgentResult:
        llm = self.llm.complete(
            system=self.system_prompt(),
            prompt=self.build_prompt(ctx) + "\nWrite landing-page hero, benefits, and CTA copy.",
            complexity="complex",
            context={"agent": self.name, "objective": ctx.objective},
        )
        copy = {
            "hero": f"Stop guessing. Start growing with {ctx.objective[:60] or 'your product'}.",
            "benefits": [
                "Set it up in minutes",
                "See the metrics that matter",
                "Grow without hiring",
            ],
            "cta": "Start free today",
            "draft": llm.text,
        }
        publish_action = {"type": "publish_live", "high_risk": True}
        return AgentResult(
            summary="Landing-page copy drafted (hero, benefits, CTA).",
            artifacts=[{"type": "landing_copy", **copy}],
            recommendation="proceed",
            requires_approval=self.needs_approval(ctx, publish_action),
            pending_action=publish_action if self.needs_approval(ctx, publish_action) else None,
            model_used=llm.model,
            token_input=llm.token_input,
            token_output=llm.token_output,
        )


# ---------------------------------------------------------------------------
# GenericAgent — default behavior for the remaining roster
# ---------------------------------------------------------------------------
class GenericAgent(BaseAgent):
    """Default LLM-report agent. Subclassed per remaining roster member."""

    def run(self, ctx: AgentContext) -> AgentResult:
        llm = self.llm.complete(
            system=self.system_prompt(),
            prompt=self.build_prompt(ctx),
            complexity=self.default_complexity,
            context={"agent": self.name, "objective": ctx.objective},
        )
        action = {"type": "domain_action", "high_risk": bool(self.high_risk_actions)}
        requires_approval = self.needs_approval(ctx, action)
        return AgentResult(
            summary=f"{self.name} produced a {self.category} report for: {ctx.objective}.",
            artifacts=[
                {
                    "type": f"{self.key}_report",
                    "summary": llm.structured.get("summary", llm.text[:200]),
                    "steps": llm.structured.get("steps", []),
                    "text": llm.text,
                }
            ],
            recommendation=llm.structured.get("recommendation", "proceed"),
            requires_approval=requires_approval,
            pending_action=action if requires_approval else None,
            model_used=llm.model,
            token_input=llm.token_input,
            token_output=llm.token_output,
        )


# Spec for every remaining roster member: (name, key, category, description,
# default_model, min_tier, complexity, high_risk_actions, required_integrations, inputs)
_GENERIC_SPECS: list[dict[str, Any]] = [
    {
        "name": "FinanceAgent",
        "key": "finance",
        "category": "strategy",
        "description": "Tracks revenue/costs/profit and forecasts cash flow, runway, and valuation.",
        "default_model": "claude-sonnet-4-6",
        "complexity": "complex",
        "high_risk_actions": ["move_money", "change_pricing"],
        "required_integrations": ["stripe"],
        "inputs": ["stripe_data", "expenses", "mrr"],
    },
    {
        "name": "Legal/ComplianceAgent",
        "key": "legal_compliance",
        "category": "strategy",
        "description": "Drafts legal docs and tracks basic compliance, flagging items for human review.",
        "default_model": "claude-opus-4-8",
        "complexity": "complex",
        "high_risk_actions": ["publish_legal_doc"],
        "required_integrations": ["google_drive"],
        "inputs": ["business_model", "jurisdictions", "data_handling"],
    },
    {
        "name": "ArchitectAgent",
        "key": "architect",
        "category": "product_eng",
        "description": "Chooses the tech stack and designs architecture and data models.",
        "default_model": "claude-opus-4-8",
        "complexity": "complex",
        "high_risk_actions": ["provision_infra"],
        "required_integrations": ["github"],
        "inputs": ["specs", "constraints", "integrations"],
    },
    {
        "name": "DevAgent",
        "key": "dev",
        "category": "product_eng",
        "description": "Writes, refactors, and tests full-stack code via repo branches and PRs.",
        "default_model": "claude-opus-4-8",
        "complexity": "complex",
        "high_risk_actions": ["merge_to_main", "production_deploy"],
        "required_integrations": ["github"],
        "inputs": ["specs", "acceptance_criteria", "repo_state"],
    },
    {
        "name": "QAAgent",
        "key": "qa",
        "category": "product_eng",
        "description": "Creates test plans, runs regression suites, files reproducible bug reports.",
        "default_model": "claude-sonnet-4-6",
        "complexity": "simple",
        "high_risk_actions": [],
        "required_integrations": ["github"],
        "inputs": ["specs", "prs", "test_history"],
    },
    {
        "name": "DevOpsAgent",
        "key": "devops",
        "category": "product_eng",
        "description": "Sets up CI/CD, manages deploys, monitors uptime, and rolls back on failure.",
        "default_model": "claude-sonnet-4-6",
        "complexity": "complex",
        "high_risk_actions": ["production_deploy"],
        "required_integrations": ["github", "vercel"],
        "inputs": ["repo", "env_configs", "health_signals"],
    },
    {
        "name": "MarketingStrategyAgent",
        "key": "marketing_strategy",
        "category": "growth",
        "description": "Picks acquisition channels and plans campaigns and content calendars.",
        "default_model": "claude-opus-4-8",
        "complexity": "complex",
        "high_risk_actions": [],
        "required_integrations": ["google_analytics"],
        "inputs": ["model", "persona", "budget"],
    },
    {
        "name": "AdsAgent",
        "key": "ads",
        "category": "growth",
        "description": "Sets up and optimizes ad campaigns within budget guardrails.",
        "default_model": "claude-sonnet-4-6",
        "complexity": "simple",
        "high_risk_actions": ["increase_daily_budget", "launch_campaign"],
        "required_integrations": ["google_ads", "meta_ads"],
        "inputs": ["budget_cap_daily", "channels", "target_audience"],
    },
    {
        "name": "SEOAgent",
        "key": "seo",
        "category": "growth",
        "description": "Keyword research plus on-page and basic technical SEO improvements.",
        "default_model": "claude-sonnet-4-6",
        "complexity": "simple",
        "high_risk_actions": ["change_live_site"],
        "required_integrations": ["google_analytics"],
        "inputs": ["site_content", "keywords", "competitors"],
    },
    {
        "name": "SalesAgent",
        "key": "sales",
        "category": "sales_support",
        "description": "Builds compliant lead lists, runs cold outreach, and books calls.",
        "default_model": "claude-sonnet-4-6",
        "complexity": "simple",
        "high_risk_actions": ["send_cold_outreach"],
        "required_integrations": ["gmail", "hubspot"],
        "inputs": ["icp", "compliance_rules", "templates"],
    },
    {
        "name": "SuccessAgent",
        "key": "success",
        "category": "sales_support",
        "description": "Designs onboarding, tracks customer health, drives retention and expansion.",
        "default_model": "claude-sonnet-4-6",
        "complexity": "simple",
        "high_risk_actions": ["send_customer_message", "offer_discount"],
        "required_integrations": ["stripe", "intercom"],
        "inputs": ["usage_data", "churn_signals", "support_history"],
    },
    {
        "name": "SupportAgent",
        "key": "support",
        "category": "sales_support",
        "description": "Answers tickets from the knowledge base and escalates complex issues.",
        "default_model": "claude-haiku-4-5",
        "complexity": "simple",
        "high_risk_actions": ["issue_refund"],
        "required_integrations": ["intercom"],
        "inputs": ["tickets", "knowledge_base", "billing_context"],
    },
    {
        "name": "OpsAgent",
        "key": "ops",
        "category": "ops_data",
        "description": "Sets up recurring tasks/SOPs and handles admin work.",
        "default_model": "claude-haiku-4-5",
        "complexity": "simple",
        "high_risk_actions": ["send_invoice_reminder"],
        "required_integrations": ["stripe", "gmail"],
        "inputs": ["calendar", "billing_data", "sop_templates"],
    },
    {
        "name": "DataAgent",
        "key": "data",
        "category": "ops_data",
        "description": "Builds dashboards and ensures data consistency across tools.",
        "default_model": "claude-sonnet-4-6",
        "complexity": "simple",
        "high_risk_actions": ["change_warehouse_schema"],
        "required_integrations": ["stripe", "google_analytics"],
        "inputs": ["source_data"],
    },
    {
        "name": "AutomationAgent",
        "key": "automation",
        "category": "ops_data",
        "description": "Connects tools and automates repetitive manual work.",
        "default_model": "claude-sonnet-4-6",
        "complexity": "simple",
        "high_risk_actions": ["activate_live_automation"],
        "required_integrations": [],
        "inputs": ["tool_inventory", "manual_workflows"],
    },
    {
        "name": "FundingReadinessAgent",
        "key": "funding_readiness",
        "category": "funding_exit",
        "description": "Prepares pitch deck, one-pager, financial model, and investor list.",
        "default_model": "claude-opus-4-8",
        "complexity": "complex",
        "high_risk_actions": ["contact_investor"],
        "required_integrations": ["google_drive"],
        "inputs": ["metrics", "strategy", "traction"],
    },
    {
        "name": "ExitPlanningAgent",
        "key": "exit_planning",
        "category": "funding_exit",
        "description": "Maintains exit readiness score and assembles due-diligence materials.",
        "default_model": "claude-opus-4-8",
        "complexity": "complex",
        "high_risk_actions": ["share_data_room"],
        "required_integrations": ["google_drive"],
        "inputs": ["financials", "kpis", "documentation_status"],
    },
    {
        "name": "AcquirerOutreachAgent",
        "key": "acquirer_outreach",
        "category": "funding_exit",
        "description": "Identifies likely acquirers and drafts outreach (founder approves).",
        "default_model": "claude-opus-4-8",
        "complexity": "complex",
        "high_risk_actions": ["send_acquirer_outreach"],
        "required_integrations": ["gmail"],
        "inputs": ["business_profile", "exit_materials", "deal_preferences"],
    },
    {
        "name": "WindDownAgent",
        "key": "wind_down",
        "category": "funding_exit",
        "description": "Manages graceful shutdown, offboarding, and asset sale.",
        "default_model": "claude-sonnet-4-6",
        "complexity": "complex",
        "high_risk_actions": ["cancel_subscriptions", "issue_refund", "sell_assets"],
        "required_integrations": ["stripe", "gmail"],
        "inputs": ["customer_list", "obligations", "asset_inventory"],
    },
    # Elite Advisor & Accelerator Layer
    {
        "name": "YC Accelerator Agent",
        "key": "yc_accelerator",
        "category": "advisor",
        "description": "PMF diagnostics, growth sprints, investor narratives, mock Q&A.",
        "default_model": "claude-opus-4-8",
        "complexity": "complex",
        "high_risk_actions": [],
        "required_integrations": [],
        "inputs": ["retention", "engagement", "revenue"],
    },
    {
        "name": "Fintech/Product Excellence Agent",
        "key": "fintech_excellence",
        "category": "advisor",
        "description": "Pricing/monetization design and unit-economics rigor on money-related work.",
        "default_model": "claude-opus-4-8",
        "complexity": "complex",
        "high_risk_actions": [],
        "required_integrations": [],
        "inputs": ["pricing", "cac", "ltv"],
    },
    {
        "name": "Deep Tech Validation Agent",
        "key": "deep_tech",
        "category": "advisor",
        "description": "Technical feasibility scoring, prior-art mapping, low-cost experiments.",
        "default_model": "claude-opus-4-8",
        "complexity": "complex",
        "high_risk_actions": [],
        "required_integrations": [],
        "inputs": ["idea", "tech_requirements"],
    },
    {
        "name": "Moonshot Strategy Agent",
        "key": "moonshot",
        "category": "advisor",
        "description": "10x framing, first-principles decomposition, backcasting, tail-risk analysis.",
        "default_model": "claude-opus-4-8",
        "complexity": "complex",
        "high_risk_actions": [],
        "required_integrations": [],
        "inputs": ["vision", "constraints"],
    },
    {
        "name": "Global Ecosystem Builder Agent",
        "key": "global_ecosystem",
        "category": "advisor",
        "description": "Market scoring, partnerships, localization, and scale strategy.",
        "default_model": "claude-opus-4-8",
        "complexity": "complex",
        "high_risk_actions": [],
        "required_integrations": [],
        "inputs": ["markets", "partnerships"],
    },
]


def _build_generic(spec: dict[str, Any]) -> type[BaseAgent]:
    attrs = {
        "key": spec["key"],
        "name": spec["name"],
        "category": spec["category"],
        "description": spec["description"],
        "default_model": spec["default_model"],
        "min_tier": spec.get("min_tier", "free"),
        "default_complexity": spec.get("complexity", "complex"),
        "high_risk_actions": spec.get("high_risk_actions", []),
        "required_integrations": spec.get("required_integrations", []),
        "inputs_schema": spec.get("inputs", []),
    }
    class_name = "".join(c for c in spec["name"] if c.isalnum()) + "Generic"
    return type(class_name, (GenericAgent,), attrs)


for _spec in _GENERIC_SPECS:
    register(_build_generic(_spec))


def roster_metadata() -> list[dict[str, Any]]:
    """Return catalog metadata for every registered agent (for the agents API)."""
    items: list[dict[str, Any]] = []
    for cls in AGENT_REGISTRY.values():
        items.append(
            {
                "agent": cls.name,
                "key": cls.key,
                "category": cls.category,
                "description": cls.description,
                "default_model": cls.default_model,
                "min_tier": cls.min_tier,
                "high_risk_actions": list(cls.high_risk_actions),
                "required_integrations": list(cls.required_integrations),
                "inputs": list(cls.inputs_schema),
            }
        )
    items.sort(key=lambda i: i["agent"])
    return items
