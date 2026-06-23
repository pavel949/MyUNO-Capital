"""Deterministic StubProvider — guarantees agents run offline with no API key.

It returns structured, sensible canned output derived deterministically from the
prompt/context, so the same input always yields the same output (good for tests
and demos).
"""

from __future__ import annotations

import hashlib
from typing import Any

from app.llm.base import LLMProvider, LLMResponse


def _seed(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16)


def _bounded(seed: int, lo: int, hi: int) -> int:
    span = hi - lo + 1
    return lo + (seed % span)


class StubProvider(LLMProvider):
    """Offline, deterministic provider."""

    name = "stub"

    def complete(
        self,
        *,
        model: str,
        system: str,
        prompt: str,
        max_tokens: int = 1024,
        context: dict[str, Any] | None = None,
    ) -> LLMResponse:
        context = context or {}
        seed = _seed(f"{system}\n{prompt}\n{sorted(context.items())!r}")

        agent = str(context.get("agent", "Agent"))
        objective = str(context.get("objective") or prompt or "the assigned objective").strip()
        objective_short = objective[:160]

        # A concise, on-domain "report" the agent can surface as its summary.
        text = (
            f"{agent} analysis (offline draft):\n"
            f"Objective: {objective_short}\n"
            f"- Assessed current context and relevant company memory.\n"
            f"- Proposed a concrete, staged plan with clear next actions.\n"
            f"- Flagged dependencies and any approval-gated steps.\n"
            f"Recommendation: proceed with the lowest-risk validating step first."
        )

        structured: dict[str, Any] = {
            "summary": (
                f"{agent} produced a plan for: {objective_short}"
                if objective_short
                else f"{agent} produced a plan."
            ),
            "steps": [
                "Gather context and constraints",
                "Draft the deliverable",
                "Identify approval-gated actions",
                "Report results and next steps",
            ],
            "recommendation": "proceed",
            "confidence": _bounded(seed, 55, 90),
        }

        return LLMResponse(
            text=text,
            model=model,
            structured=structured,
            token_input=max(1, len(prompt) // 4),
            token_output=max(1, len(text) // 4),
            provider=self.name,
        )
