import base64
import textwrap
import wave
from pathlib import Path

import pytest

from app.render.renderer import RenderRequest, Renderer


PNG_PIXEL = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9sXl16sAAAAASUVORK5CYII="
)


def test_renderer_writes_video_with_fake_ffmpeg(tmp_path: Path) -> None:
    ffmpeg_binary = _build_fake_ffmpeg(tmp_path, mode="write")
    request = _build_render_request(tmp_path)
    renderer = Renderer(ffmpeg_binary=str(ffmpeg_binary), work_dir=tmp_path)

    result = renderer.render(request)

    assert result.status == "completed"
    assert Path(result.video_path).exists()
    assert Path(result.video_path).read_bytes() == b"fake-video"


def test_renderer_raises_when_ffmpeg_does_not_create_output(tmp_path: Path) -> None:
    ffmpeg_binary = _build_fake_ffmpeg(tmp_path, mode="noop")
    request = _build_render_request(tmp_path)
    renderer = Renderer(ffmpeg_binary=str(ffmpeg_binary), work_dir=tmp_path)

    with pytest.raises(RuntimeError, match="did not produce an output file"):
        renderer.render(request)


def test_renderer_returns_degraded_result_when_placeholder_mode_is_enabled(tmp_path: Path) -> None:
    request = _build_render_request(tmp_path)
    renderer = Renderer(
        ffmpeg_binary="ffmpeg-missing",
        work_dir=tmp_path,
        allow_placeholder_when_unavailable=True,
    )

    result = renderer.render(request)

    assert result.status == "degraded"
    assert result.video_path == ""
    assert result.manifest["placeholder"] is True


def _build_fake_ffmpeg(tmp_path: Path, *, mode: str) -> Path:
    script_path = tmp_path / f"fake_ffmpeg_{mode}.py"
    script_path.write_text(
        textwrap.dedent(
            f"""
            import pathlib
            import sys

            mode = {mode!r}
            output_path = pathlib.Path(sys.argv[-1])
            if mode == "write":
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(b"fake-video")
            sys.exit(0)
            """
        ).strip(),
        encoding="utf-8",
    )

    command_path = tmp_path / f"fake_ffmpeg_{mode}.cmd"
    command_path.write_text(
        textwrap.dedent(
            f"""
            @echo off
            python "{script_path}" %*
            """
        ).strip(),
        encoding="utf-8",
    )
    return command_path


def _build_render_request(tmp_path: Path) -> RenderRequest:
    image_path = tmp_path / "image.png"
    image_path.write_bytes(PNG_PIXEL)

    voice_path = tmp_path / "voice.wav"
    with wave.open(str(voice_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(24000)
        wav_file.writeframes(b"\x00\x00" * 24000)

    return RenderRequest(
        job_id="render-test",
        topic="渲染烟雾测试",
        script="这是一段用于验证渲染器输出的占位文案。",
        storyboard=[{"shot": "1", "caption": "占位镜头"}],
        visual_assets=[str(image_path)],
        voice_asset=str(voice_path),
        subtitles_enabled=True,
        aspect_ratio="9:16",
    )
