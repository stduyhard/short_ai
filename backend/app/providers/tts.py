from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol


@dataclass(slots=True, frozen=True)
class TTSRequest:
    text: str
    voice: str = "default"
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class TTSResponse:
    asset_uri: str
    provider_name: str


class TTSProvider(Protocol):
    provider_name: str

    def synthesize(self, request: TTSRequest) -> TTSResponse:
        """Return a reference to a synthesized voice asset."""
