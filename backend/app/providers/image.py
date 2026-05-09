from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol


@dataclass(slots=True, frozen=True)
class ImageRequest:
    prompt: str
    size: str = "1024x1024"
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ImageResponse:
    asset_uri: str
    provider_name: str


class ImageProvider(Protocol):
    provider_name: str

    def generate(self, request: ImageRequest) -> ImageResponse:
        """Return a reference to a generated image asset."""
