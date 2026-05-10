from __future__ import annotations

import shutil
from dataclasses import dataclass

from app.core.config import Settings


@dataclass(slots=True, frozen=True)
class RuntimeReadiness:
    providers_configured: bool
    ffmpeg_available: bool

    @property
    def ready_for_real_generation(self) -> bool:
        return self.providers_configured and self.ffmpeg_available

    def to_response(self) -> dict[str, bool]:
        return {
            "providersConfigured": self.providers_configured,
            "ffmpegAvailable": self.ffmpeg_available,
            "readyForRealGeneration": self.ready_for_real_generation,
        }


def inspect_runtime_readiness(settings: Settings) -> RuntimeReadiness:
    return RuntimeReadiness(
        providers_configured=_providers_are_configured(settings),
        ffmpeg_available=shutil.which(settings.ffmpeg_binary) is not None,
    )


def _providers_are_configured(settings: Settings) -> bool:
    return all(
        [
            _provider_is_configured(settings.llm_provider, openai_api_key=settings.openai_api_key, dashscope_api_key=settings.dashscope_api_key),
            _provider_is_configured(settings.image_provider, openai_api_key=settings.openai_api_key, dashscope_api_key=settings.dashscope_api_key),
            _provider_is_configured(settings.tts_provider, openai_api_key=settings.openai_api_key, dashscope_api_key=settings.dashscope_api_key),
        ]
    )


def _provider_is_configured(provider: str, *, openai_api_key: str | None, dashscope_api_key: str | None) -> bool:
    if provider == "stub":
        return False
    if provider == "openai":
        return bool(openai_api_key)
    if provider == "qwen":
        return bool(dashscope_api_key)
    return False
