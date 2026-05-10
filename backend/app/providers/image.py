from __future__ import annotations

import base64
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Mapping, Protocol

import httpx
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


class StubImageProvider:
    provider_name = "stub"

    def __init__(self, storage_provider: StorageProvider) -> None:
        self._storage_provider = storage_provider

    def generate(self, request: ImageRequest) -> ImageResponse:
        job_id = request.metadata.get("job_id", "adhoc")
        stored = self._storage_provider.save_bytes(
            path=f"images/{job_id}/generated.png",
            content=base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9sXl16sAAAAASUVORK5CYII="
            ),
            content_type="image/png",
            metadata={"provider": self.provider_name},
        )
        return ImageResponse(asset_uri=stored.path, provider_name=self.provider_name)


class QwenImageProvider:
    provider_name = "qwen"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str,
        storage_provider: StorageProvider,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._storage_provider = storage_provider

    def generate(self, request: ImageRequest) -> ImageResponse:
        response = httpx.post(
            f"{self._base_url}/services/aigc/text2image/image-synthesis",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "false",
            },
            json={
                "model": self._model,
                "input": {"prompt": request.prompt},
                "parameters": {"size": request.size},
            },
            timeout=120.0,
        )
        response.raise_for_status()
        payload = response.json()
        image_url = _extract_qwen_image_url(payload)
        image_response = httpx.get(image_url, timeout=120.0)
        image_response.raise_for_status()
        job_id = request.metadata.get("job_id", "adhoc")
        target_name = Path(image_url).name or "generated.png"
        stored = self._storage_provider.save_bytes(
            path=f"images/{job_id}/{target_name}",
            content=image_response.content,
            content_type=image_response.headers.get("content-type", "image/png"),
            metadata={"provider": self.provider_name},
        )
        return ImageResponse(asset_uri=stored.path, provider_name=self.provider_name)


def _extract_qwen_image_url(payload: Mapping[str, object]) -> str:
    output = payload.get("output")
    if not isinstance(output, Mapping):
        raise ValueError("Qwen image generation returned no output payload")

    results = output.get("results")
    if isinstance(results, list) and results:
        first = results[0]
        if isinstance(first, Mapping):
            url = first.get("url")
            if isinstance(url, str) and url:
                return url

    raise ValueError("Qwen image generation returned no image URL")
