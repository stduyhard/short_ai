from __future__ import annotations

import shutil
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RuntimeReadiness:
    openai_configured: bool
    ffmpeg_available: bool

    @property
    def ready_for_real_generation(self) -> bool:
        return self.openai_configured and self.ffmpeg_available

    def to_response(self) -> dict[str, bool]:
        return {
            "openaiConfigured": self.openai_configured,
            "ffmpegAvailable": self.ffmpeg_available,
            "readyForRealGeneration": self.ready_for_real_generation,
        }


def inspect_runtime_readiness(*, openai_api_key: str | None, ffmpeg_binary: str) -> RuntimeReadiness:
    return RuntimeReadiness(
        openai_configured=bool(openai_api_key),
        ffmpeg_available=shutil.which(ffmpeg_binary) is not None,
    )
