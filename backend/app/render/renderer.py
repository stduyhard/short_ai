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
    video_segments: list[str]
    voice_asset: str
    subtitles_enabled: bool
    aspect_ratio: str


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
        manifest: dict[str, object] = {
            "job_id": request.job_id,
            "topic": request.topic,
            "script": request.script,
            "storyboard": request.storyboard,
            "visual_assets": request.visual_assets,
            "video_segments": request.video_segments,
            "voice_asset": request.voice_asset,
            "subtitles_enabled": request.subtitles_enabled,
            "aspect_ratio": request.aspect_ratio,
            "video_path": str(video_path),
        }

        if self._allow_placeholder_when_unavailable:
            manifest["placeholder"] = True
            manifest["warning"] = "Placeholder render mode is enabled because not all providers are real."
            return RenderResult(status="degraded", video_path="", manifest=manifest)

        command, command_manifest = self._build_command(render_dir, video_path, request)
        manifest["ffmpeg_command"] = command
        manifest.update(command_manifest)

        try:
            completed = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
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
        if not request.video_segments:
            raise ValueError("video_segments is required")
        if not request.voice_asset.strip():
            raise ValueError("voice_asset is required")

    def _build_command(
        self,
        render_dir: Path,
        video_path: Path,
        request: RenderRequest,
    ) -> tuple[list[str], dict[str, object]]:
        filter_chain = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
        voice_asset = str(Path(request.voice_asset).resolve())
        concat_file = self._write_video_concat_manifest(render_dir, request.video_segments)
        return (
            [
                self._ffmpeg_binary,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-i",
                voice_asset,
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-vf",
                filter_chain,
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                str(video_path),
            ],
            {
                "render_mode": "concat-video-segments",
                "concat_manifest": str(concat_file),
            },
        )

    @staticmethod
    def _write_concat_manifest(render_dir: Path, visual_assets: list[str], per_asset_duration: float) -> Path:
        render_dir.mkdir(parents=True, exist_ok=True)
        concat_file = render_dir / "inputs.txt"
        lines: list[str] = []
        for asset in visual_assets:
            normalized = Path(asset).resolve()
            lines.append(f"file '{normalized.as_posix()}'")
            lines.append(f"duration {per_asset_duration:.3f}")
        if visual_assets:
            last_asset = Path(visual_assets[-1]).resolve()
            lines.append(f"file '{last_asset.as_posix()}'")
        concat_file.write_text("\n".join(lines), encoding="utf-8")
        return concat_file

    @staticmethod
    def _write_video_concat_manifest(render_dir: Path, video_segments: list[str]) -> Path:
        render_dir.mkdir(parents=True, exist_ok=True)
        concat_file = render_dir / "video-segments.txt"
        lines = [f"file '{Path(segment).resolve().as_posix()}'" for segment in video_segments]
        concat_file.write_text("\n".join(lines), encoding="utf-8")
        return concat_file

    def _probe_media_duration(self, media_path: str) -> float:
        ffprobe_binary = self._resolve_ffprobe_binary()
        completed = subprocess.run(
            [
                ffprobe_binary,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                media_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        duration_text = completed.stdout.strip()
        if not duration_text:
            raise RuntimeError(f"Could not determine media duration for {media_path}")
        return float(duration_text)

    def _resolve_ffprobe_binary(self) -> str:
        ffmpeg_path = Path(self._ffmpeg_binary)
        if ffmpeg_path.suffix.lower() == ".exe":
            sibling = ffmpeg_path.with_name("ffprobe.exe")
            if sibling.exists():
                return str(sibling)
        return "ffprobe"
