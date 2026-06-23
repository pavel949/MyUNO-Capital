"""Agent roster + execution tests — run offline via the StubProvider."""

from __future__ import annotations

from app.agents.base import AgentContext, AutonomyProfile
from app.agents.registry import (
    AGENT_REGISTRY,
    ContentAgent,
    IdeaValidationAgent,
    ProductManagerAgent,
    StrategyAgent,
    roster_metadata,
)
from app.llm.router import LLMRouter


def test_full_roster_registered() -> None:
    meta = roster_metadata()
    names = {m["agent"] for m in meta}
    # Functional team (23) + Elite Advisor layer (5) == 28 agents in agents.md.
    assert len(AGENT_REGISTRY) == 28
    for expected in [
        "IdeaValidationAgent",
        "StrategyAgent",
        "ProductManagerAgent",
        "ContentAgent",
        "DevAgent",
        "AdsAgent",
        "ExitPlanningAgent",
        "YC Accelerator Agent",
        "Moonshot Strategy Agent",
    ]:
        assert expected in names


def test_router_uses_stub_without_real_key() -> None:
    router = LLMRouter()
    assert router.active_provider_name == "stub"
    resp = router.complete(system="s", prompt="hello", complexity="complex")
    assert resp.provider == "stub"
    assert resp.text


def test_idea_validation_produces_scores() -> None:
    agent = IdeaValidationAgent(llm=LLMRouter())
    ctx = AgentContext(
        tenant_id="t",
        business_id="b",
        objective="AI bookkeeping for freelancers",
        inputs={"factors": {"market_size": 80, "competition": 40}},
    )
    result = agent.run(ctx)
    assert 0 <= result.scores["risk"] <= 100
    assert 0 <= result.scores["complexity"] <= 100
    assert 0 <= result.scores["potential"] <= 100
    assert "advisor_scores" in result.scores
    assert result.scores["overall_call"]


def test_strategy_generates_okrs() -> None:
    agent = StrategyAgent(llm=LLMRouter())
    ctx = AgentContext(
        tenant_id="t", business_id="b", objective="Reach $10k MRR", inputs={"metric": "mrr"}
    )
    okrs = agent.generate_okrs(ctx)
    assert len(okrs) >= 1
    assert "objective" in okrs[0]
    assert okrs[0]["key_results"]


def test_pm_and_content_run() -> None:
    pm = ProductManagerAgent(llm=LLMRouter())
    pm_result = pm.run(AgentContext(tenant_id="t", business_id="b", objective="Plan MVP"))
    assert pm_result.artifacts

    content = ContentAgent(llm=LLMRouter())
    c_result = content.run(
        AgentContext(
            tenant_id="t",
            business_id="b",
            objective="Write landing page",
            autonomy=AutonomyProfile.ASK_FIRST,
        )
    )
    # ask_first means the publish action requires approval.
    assert c_result.requires_approval is True


def test_generic_agent_runs() -> None:
    cls = AGENT_REGISTRY["DevAgent"]
    agent = cls(llm=LLMRouter())
    result = agent.run(
        AgentContext(
            tenant_id="t",
            business_id="b",
            objective="Implement Stripe checkout",
            autonomy=AutonomyProfile.GUIDED,
        )
    )
    assert result.summary
    assert result.artifacts
