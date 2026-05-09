from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
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
    def __init__(
        self,
        *,
        ffmpeg_binary: str = "ffmpeg",
        work_dir: Path | None = None,
        allow_placeholder_when_unavailable: bool = False,
    ) -> None:
        self._ffmpeg_binary = ffmpeg_binary
        self._work_dir = work_dir or Path("artifacts")
        self._allow_placeholder_when_unavailable = allow_placeholder_when_unavailable
        self._work_dir.mkdir(parents=True, exist_ok=True)

    def render(self, request: RenderRequest) -> RenderResult:
        self._validate_request(request)

        render_dir = self._work_dir / "renders" / request.job_id
        render_dir.mkdir(parents=True, exist_ok=True)
        video_path = render_dir / "final.mp4"
        concat_file = self._write_concat_manifest(render_dir, request.visual_assets)
        command = [
            self._ffmpeg_binary,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-i",
            request.voice_asset,
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(video_path),
        ]
        manifest: dict[str, object] = {
            "job_id": request.job_id,
            "topic": request.topic,
            "script": request.script,
            "storyboard": request.storyboard,
            "visual_assets": request.visual_assets,
            "voice_asset": request.voice_asset,
            "video_path": str(video_path),
            "ffmpeg_command": command,
        }

        try:
            completed = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            if self._allow_placeholder_when_unavailable:
                manifest["placeholder"] = True
                manifest["warning"] = (
                    f"FFmpeg binary not found: {self._ffmpeg_binary}. Returned placeholder render result."
                )
                return RenderResult(status="degraded", video_path="", manifest=manifest)
            raise FileNotFoundError(
                f"FFmpeg binary not found: {self._ffmpeg_binary}. Set FFMPEG_BINARY or install ffmpeg."
            ) from exc

        manifest["ffmpeg_stdout"] = completed.stdout
        manifest["ffmpeg_stderr"] = completed.stderr
        if not video_path.exists():
            raise RuntimeError(
                f"FFmpeg command completed successfully but did not produce an output file: {video_path}"
            )
        return RenderResult(status="completed", video_path=str(video_path), manifest=manifest)

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

    @staticmethod
    def _write_concat_manifest(render_dir: Path, visual_assets: list[str]) -> Path:
        concat_file = render_dir / "inputs.txt"
        lines: list[str] = []
        for asset in visual_assets:
            normalized = Path(asset).resolve()
            lines.append(f"file '{normalized.as_posix()}'")
            lines.append("duration 3")
        if lines:
            lines.pop()
        concat_file.write_text("\n".join(lines), encoding="utf-8")
        return concat_file
