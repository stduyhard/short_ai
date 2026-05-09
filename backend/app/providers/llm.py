from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol


@dataclass(slots=True, frozen=True)
class LLMRequest:
    prompt: str
    system_prompt: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class LLMResponse:
    content: str
    provider_name: str


class LLMProvider(Protocol):
    provider_name: str

    def generate(self, request: LLMRequest) -> LLMResponse:
        """Return generated text for the supplied prompt."""
