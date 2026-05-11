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


def test_renderer_uses_concat_mode_for_video_segments(tmp_path: Path) -> None:
    renderer = Renderer(ffmpeg_binary="ffmpeg", work_dir=tmp_path)
    request = _build_render_request(tmp_path)

    command, manifest = renderer._build_command(tmp_path / "renders", tmp_path / "final.mp4", request)

    assert manifest["render_mode"] == "concat-video-segments"
    assert "-f" in command
    assert "concat" in command


def test_renderer_concat_manifest_repeats_last_asset_for_duration(tmp_path: Path) -> None:
    image_path = tmp_path / "image.png"
    image_path.write_bytes(PNG_PIXEL)
    concat_file = Renderer._write_concat_manifest(tmp_path, [str(image_path)], 3.0)

    assert concat_file.read_text(encoding="utf-8").splitlines() == [
        f"file '{image_path.resolve().as_posix()}'",
        "duration 3.000",
        f"file '{image_path.resolve().as_posix()}'",
    ]


def test_renderer_uses_concat_mode_for_multiple_visual_assets(tmp_path: Path) -> None:
    renderer = Renderer(ffmpeg_binary="ffmpeg", work_dir=tmp_path)
    request = _build_render_request(tmp_path, image_count=3)

    command, manifest = renderer._build_command(tmp_path / "renders", tmp_path / "final.mp4", request)

    assert manifest["render_mode"] == "concat-video-segments"
    assert "-f" in command
    assert "concat" in command


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


def _build_render_request(tmp_path: Path, *, image_count: int = 1) -> RenderRequest:
    image_paths: list[str] = []
    segment_paths: list[str] = []
    for index in range(image_count):
        image_path = tmp_path / f"image-{index}.png"
        image_path.write_bytes(PNG_PIXEL)
        image_paths.append(str(image_path))
        segment_path = tmp_path / f"segment-{index}.mp4"
        segment_path.write_bytes(b"fake-segment")
        segment_paths.append(str(segment_path))

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
        visual_assets=image_paths,
        video_segments=segment_paths,
        voice_asset=str(voice_path),
        subtitles_enabled=True,
        aspect_ratio="9:16",
    )
