"""LLM router: selects a provider and model tier, with offline-safe fallback.

- If no real Anthropic key is configured -> StubProvider for everything.
- Otherwise route by complexity: DEFAULT_LLM_MODEL for complex tasks,
  LLM_FALLBACK_MODEL for simple ones.
- Any provider error falls back to the StubProvider so agents always complete.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from app.config import settings
from app.llm.anthropic_provider import AnthropicProvider
from app.llm.base import LLMProvider, LLMResponse
from app.llm.stub import StubProvider

logger = logging.getLogger("myuno.llm")


class LLMRouter:
    def __init__(self) -> None:
        self._stub = StubProvider()
        self._anthropic: LLMProvider | None = None

        if settings.has_real_anthropic_key and AnthropicProvider.available():
            try:
                self._anthropic = AnthropicProvider(settings.anthropic_api_key)
            except Exception as exc:  # pragma: no cover
                logger.warning("Anthropic provider init failed, using stub: %s", exc)
                self._anthropic = None

    @property
    def active_provider_name(self) -> str:
        return "anthropic" if self._anthropic is not None else "stub"

    def select_model(self, complexity: str = "complex") -> str:
        """Map task complexity to a concrete model name."""
        if complexity in ("simple", "fast", "low"):
            return settings.llm_fallback_model
        return settings.default_llm_model

    def complete(
        self,
        *,
        system: str,
        prompt: str,
        complexity: str = "complex",
        max_tokens: int = 1024,
        context: dict[str, Any] | None = None,
    ) -> LLMResponse:
        model = self.select_model(complexity)

        if self._anthropic is not None:
            try:
                return self._anthropic.complete(
                    model=model,
                    system=system,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    context=context,
                )
            except Exception as exc:  # pragma: no cover - network/runtime errors
                logger.warning("Anthropic completion failed, falling back to stub: %s", exc)

        return self._stub.complete(
            model=model,
            system=system,
            prompt=prompt,
            max_tokens=max_tokens,
            context=context,
        )


@lru_cache
def get_llm_router() -> LLMRouter:
    return LLMRouter()
