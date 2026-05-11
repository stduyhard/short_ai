from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Protocol

import httpx

from app.providers.storage import StorageProvider


@dataclass(slots=True, frozen=True)
class VideoSegmentRequest:
    image_path: str
    prompt: str
    duration_seconds: float
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class VideoSegmentResponse:
    asset_uri: str
    provider_name: str


class VideoProvider(Protocol):
    provider_name: str

    def generate_segment(self, request: VideoSegmentRequest) -> VideoSegmentResponse:
        """Return a reference to a generated video segment asset."""


class StubVideoProvider:
    provider_name = "stub"

    def __init__(self, storage_provider: StorageProvider) -> None:
        self._storage_provider = storage_provider

    def generate_segment(self, request: VideoSegmentRequest) -> VideoSegmentResponse:
        job_id = request.metadata.get("job_id", "adhoc")
        shot_id = request.metadata.get("shot", "1")
        stored = self._storage_provider.save_bytes(
            path=f"video-segments/{job_id}/shot-{shot_id}.mp4",
            content=b"stub-video-segment",
            content_type="video/mp4",
            metadata={"provider": self.provider_name},
        )
        return VideoSegmentResponse(asset_uri=stored.path, provider_name=self.provider_name)


class QwenVideoProvider:
    provider_name = "qwen"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str,
        storage_provider: StorageProvider,
        poll_interval_seconds: float = 2.0,
        timeout_seconds: float = 300.0,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._storage_provider = storage_provider
        self._poll_interval_seconds = poll_interval_seconds
        self._timeout_seconds = timeout_seconds

    def generate_segment(self, request: VideoSegmentRequest) -> VideoSegmentResponse:
        task_id = self._submit_task(request)
        video_url = self._wait_for_video_url(task_id)
        video_response = httpx.get(video_url, timeout=300.0)
        video_response.raise_for_status()
        job_id = request.metadata.get("job_id", "adhoc")
        shot_id = request.metadata.get("shot", "1")
        stored = self._storage_provider.save_bytes(
            path=f"video-segments/{job_id}/shot-{shot_id}.mp4",
            content=video_response.content,
            content_type=video_response.headers.get("content-type", "video/mp4"),
            metadata={"provider": self.provider_name, "task_id": task_id},
        )
        return VideoSegmentResponse(asset_uri=stored.path, provider_name=self.provider_name)

    def _submit_task(self, request: VideoSegmentRequest) -> str:
        response = httpx.post(
            f"{self._base_url}/services/aigc/video-generation/video-synthesis",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable",
            },
            json={
                "model": self._model,
                "input": {
                    "prompt": request.prompt,
                    "img_url": _image_path_to_data_url(request.image_path),
                },
                "parameters": {
                    "duration": _normalize_segment_duration(request.duration_seconds),
                    "resolution": "720P",
                    "prompt_extend": True,
                    "watermark": False,
                },
            },
            timeout=120.0,
        )
        response.raise_for_status()
        payload = response.json()
        output = payload.get("output")
        if not isinstance(output, Mapping):
            raise ValueError("Qwen video generation returned no output payload")
        task_id = output.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("Qwen video generation returned no task_id")
        return task_id

    def _wait_for_video_url(self, task_id: str) -> str:
        deadline = time.monotonic() + self._timeout_seconds
        while time.monotonic() < deadline:
            response = httpx.get(
                f"{self._base_url}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=60.0,
            )
            response.raise_for_status()
            payload = response.json()
            task_status = str(payload.get("output", {}).get("task_status", "")).upper()
            if task_status == "SUCCEEDED":
                return _extract_qwen_video_url(payload)
            if task_status in {"FAILED", "CANCELED"}:
                task_results = payload.get("output", {}).get("task_results")
                detail = json.dumps(task_results, ensure_ascii=False) if task_results else "unknown error"
                raise RuntimeError(f"Qwen video generation failed for task {task_id}: {detail}")
            time.sleep(self._poll_interval_seconds)
        raise TimeoutError(f"Timed out waiting for Qwen video task {task_id}")


def _normalize_segment_duration(duration_seconds: float) -> int:
    rounded = int(round(duration_seconds))
    return max(2, min(15, rounded))


def _image_path_to_data_url(image_path: str) -> str:
    source = Path(image_path)
    suffix = source.suffix.lower()
    mime_type = "image/png"
    if suffix in {".jpg", ".jpeg"}:
        mime_type = "image/jpeg"
    elif suffix == ".webp":
        mime_type = "image/webp"
    return f"data:{mime_type};base64,{base64.b64encode(source.read_bytes()).decode('ascii')}"


def _extract_qwen_video_url(payload: Mapping[str, object]) -> str:
    output = payload.get("output")
    if not isinstance(output, Mapping):
        raise ValueError("Qwen video generation returned no output payload")

    task_results = output.get("task_results")
    if isinstance(task_results, list):
        for result in task_results:
            if isinstance(result, Mapping):
                video_url = result.get("video_url")
                if isinstance(video_url, str) and video_url:
                    return video_url
                output_video_url = result.get("output_video_url")
                if isinstance(output_video_url, str) and output_video_url:
                    return output_video_url

    video_url = output.get("video_url")
    if isinstance(video_url, str) and video_url:
        return video_url

    raise ValueError("Qwen video generation returned no video URL")
