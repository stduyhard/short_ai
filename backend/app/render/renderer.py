from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(slots=True, frozen=True)
class RenderRequest:
    job_id: str
    topic: str
    script: str
    storyboard: list[dict[str, str]]
    visual_assets: list[str]
    voice_asset: str


@dataclass(slots=True, frozen=True)
class RenderResult:
    status: str
    video_path: str
    manifest: Mapping[str, object]


class Renderer:
    def render(self, request: RenderRequest) -> RenderResult:
        self._validate_request(request)

        video_path = f"renders/{request.job_id}/final.mp4"
        manifest = {
            "job_id": request.job_id,
            "topic": request.topic,
            "script": request.script,
            "storyboard": request.storyboard,
            "visual_assets": request.visual_assets,
            "voice_asset": request.voice_asset,
            "video_path": video_path,
        }

        return RenderResult(status="queued", video_path=video_path, manifest=manifest)

    @staticmethod
    def _validate_request(request: RenderRequest) -> None:
        if not request.job_id.strip():
            raise ValueError("job_id is required")
        if not request.topic.strip():
            raise ValueError("topic is required")
        if not request.script.strip():
            raise ValueError("script is required")
        if not request.storyboard:
            raise ValueError("storyboard is required")
        if not request.visual_assets:
            raise ValueError("visual_assets is required")
        if not request.voice_asset.strip():
            raise ValueError("voice_asset is required")
