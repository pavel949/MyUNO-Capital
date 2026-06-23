"""Provider-agnostic LLM interface."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMResponse:
    """Normalized response from any provider."""

    text: str
    model: str
    structured: dict[str, Any] = field(default_factory=dict)
    token_input: int = 0
    token_output: int = 0
    provider: str = "stub"


class LLMProvider(abc.ABC):
    """Base interface every LLM provider implements."""

    name: str = "base"

    @abc.abstractmethod
    def complete(
        self,
        *,
        model: str,
        system: str,
        prompt: str,
        max_tokens: int = 1024,
        context: dict[str, Any] | None = None,
    ) -> LLMResponse:
        """Return a completion. Implementations must never raise on bad input;
        they should degrade gracefully (the router also wraps this in fallback).
        """
        ...
