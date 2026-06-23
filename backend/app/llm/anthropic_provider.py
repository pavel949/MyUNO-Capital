"""Anthropic provider — used only when a real API key is configured.

The `anthropic` import is guarded so the app imports and runs without the SDK
installed or without a key. On any error the router falls back to the stub.
"""

from __future__ import annotations

from typing import Any

from app.llm.base import LLMProvider, LLMResponse

try:  # guarded import — never crash if SDK is missing
    import anthropic  # type: ignore

    _ANTHROPIC_AVAILABLE = True
except Exception:  # pragma: no cover - exercised only without the SDK
    anthropic = None  # type: ignore
    _ANTHROPIC_AVAILABLE = False


class AnthropicProvider(LLMProvider):
    """Thin wrapper over the Anthropic Messages API."""

    name = "anthropic"

    def __init__(self, api_key: str):
        if not _ANTHROPIC_AVAILABLE:
            raise RuntimeError("anthropic SDK is not installed")
        self._client = anthropic.Anthropic(api_key=api_key)

    @staticmethod
    def available() -> bool:
        return _ANTHROPIC_AVAILABLE

    def complete(
        self,
        *,
        model: str,
        system: str,
        prompt: str,
        max_tokens: int = 1024,
        context: dict[str, Any] | None = None,
    ) -> LLMResponse:
        message = self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        # Concatenate text blocks from the response content.
        parts = []
        for block in getattr(message, "content", []) or []:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        text = "\n".join(parts) if parts else ""

        usage = getattr(message, "usage", None)
        token_input = getattr(usage, "input_tokens", 0) if usage else 0
        token_output = getattr(usage, "output_tokens", 0) if usage else 0

        return LLMResponse(
            text=text,
            model=model,
            structured={"summary": text[:280]},
            token_input=token_input or 0,
            token_output=token_output or 0,
            provider=self.name,
        )
