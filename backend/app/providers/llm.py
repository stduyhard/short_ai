from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol

from openai import OpenAI


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


class OpenAILLMProvider:
    provider_name = "openai"

    def __init__(self, *, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def generate(self, request: LLMRequest) -> LLMResponse:
        response = self._client.responses.create(
            model=self._model,
            instructions=request.system_prompt,
            input=request.prompt,
        )
        return LLMResponse(content=response.output_text, provider_name=self.provider_name)


class StubLLMProvider:
    provider_name = "stub"

    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content=f"stub::{request.metadata.get('purpose', 'text')}::{request.prompt[:80]}",
            provider_name=self.provider_name,
        )
