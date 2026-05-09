from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Literal, Mapping, Protocol

from openai import OpenAI

from app.providers.storage import StorageProvider


ImageSize = Literal[
    "256x256",
    "512x512",
    "1024x1024",
    "1024x1536",
    "1536x1024",
]


@dataclass(slots=True, frozen=True)
class ImageRequest:
    prompt: str
    size: ImageSize = "1024x1024"
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ImageResponse:
    asset_uri: str
    provider_name: str


class ImageProvider(Protocol):
    provider_name: str

    def generate(self, request: ImageRequest) -> ImageResponse:
        """Return a reference to a generated image asset."""


class OpenAIImageProvider:
    provider_name = "openai"

    def __init__(self, *, api_key: str, model: str, storage_provider: StorageProvider) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._storage_provider = storage_provider

    def generate(self, request: ImageRequest) -> ImageResponse:
        response = self._client.images.generate(
            model=self._model,
            prompt=request.prompt,
            size=request.size,
            response_format="b64_json",
            output_format="png",
        )

        if not response.data:
            raise ValueError("OpenAI image generation returned no data")

        image = response.data[0]
        if image.b64_json:
            content = base64.b64decode(image.b64_json)
            stored = self._storage_provider.save_bytes(
                path=f"images/{request.metadata.get('job_id', 'adhoc')}/generated.png",
                content=content,
                content_type="image/png",
                metadata={"provider": self.provider_name},
            )
            return ImageResponse(asset_uri=stored.path, provider_name=self.provider_name)

        if image.url is None:
            raise ValueError("OpenAI image generation returned neither b64_json nor url")

        return ImageResponse(asset_uri=image.url, provider_name=self.provider_name)
