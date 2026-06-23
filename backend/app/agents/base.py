"""BaseAgent — the common interface for every MyUNO Capital agent.

Mirrors the skeleton in agents.md (perceive -> plan -> act -> reflect -> report)
but uses the synchronous stack (sync SQLAlchemy + sync LLM router). Agents have
access to the LLM router, a DB session, and a memory helper, plus autonomy gating.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from sqlalchemy.orm import Session

from app.llm.router import LLMRouter


class ModelTier(str, Enum):
    """Routing tiers mapped to concrete models by the LLM router."""

    COMPLEX = "complex"
    MID = "complex"  # the workhorse still routes to the default model
    FAST = "simple"


class AutonomyProfile(str, Enum):
    ASK_FIRST = "ask_first"
    GUIDED = "guided"
    AUTONOMOUS = "autonomous_within_limits"


@dataclass
class AgentContext:
    """Everything an agent needs to perceive its world."""

    tenant_id: str
    business_id: str
    objective: str
    inputs: dict[str, Any] = field(default_factory=dict)
    autonomy: AutonomyProfile = AutonomyProfile.ASK_FIRST
    guardrails: dict[str, Any] = field(default_factory=dict)
    memory: list[str] = field(default_factory=list)


@dataclass
class AgentResult:
    summary: str
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    recommendation: str | None = None
    requires_approval: bool = False
    pending_action: dict[str, Any] | None = None
    scores: dict[str, Any] = field(default_factory=dict)
    model_used: str | None = None
    token_input: int = 0
    token_output: int = 0


class BaseAgent(abc.ABC):
    """Base class for all agents."""

    key: str = "base"
    name: str = "BaseAgent"
    category: str = "strategy"
    description: str = "Base agent."
    default_model: str = "claude-sonnet-4-6"
    min_tier: str = "free"
    default_complexity: str = "complex"
    high_risk_actions: list[str] = []
    required_integrations: list[str] = []
    inputs_schema: list[str] = []

    def __init__(self, llm: LLMRouter, db: Session | None = None, memory: Any = None):
        self.llm = llm
        self.db = db
        self.memory = memory

    # --- lifecycle helpers -------------------------------------------------

    def system_prompt(self) -> str:
        return (
            f"You are the {self.name} on a solo founder's autonomous AI team. "
            f"Category: {self.category}. {self.description} "
            f"Follow the perceive -> plan -> act -> reflect -> report lifecycle. "
            f"Be concrete, concise, and actionable."
        )

    def build_prompt(self, ctx: AgentContext) -> str:
        lines = [f"Objective: {ctx.objective}"]
        if ctx.inputs:
            lines.append(f"Inputs: {ctx.inputs}")
        if ctx.memory:
            lines.append("Relevant memory:\n- " + "\n- ".join(ctx.memory[:5]))
        lines.append("Produce a clear plan, deliverables, and a recommendation.")
        return "\n".join(lines)

    def needs_approval(self, ctx: AgentContext, action: dict[str, Any]) -> bool:
        """High-risk or guardrail-breaching actions require human approval."""
        if ctx.autonomy is AutonomyProfile.ASK_FIRST:
            return True
        if action.get("high_risk"):
            if ctx.autonomy is AutonomyProfile.AUTONOMOUS:
                return self._breaches_guardrail(ctx, action)
            return True
        return self._breaches_guardrail(ctx, action)

    def _breaches_guardrail(self, ctx: AgentContext, action: dict[str, Any]) -> bool:
        cap = ctx.guardrails.get("ad_spend_daily_cap_cents")
        spend = action.get("ad_spend_daily_cents")
        if cap is not None and spend is not None and spend > cap:
            return True
        daily_usd_cap = ctx.guardrails.get("ads_daily_usd")
        daily_usd = action.get("ads_daily_usd")
        if daily_usd_cap is not None and daily_usd is not None and daily_usd > daily_usd_cap:
            return True
        return False

    @abc.abstractmethod
    def run(self, ctx: AgentContext) -> AgentResult:
        """Main entry point invoked by the orchestrator."""
        ...
