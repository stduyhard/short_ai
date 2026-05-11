from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Mapping, Literal

from pydantic import BaseModel


ProviderName = Literal["stub", "openai", "qwen"]


class Settings(BaseModel):
    app_name: str = "short-video-backend"

    llm_provider: ProviderName = "stub"
    image_provider: ProviderName = "stub"
    tts_provider: ProviderName = "stub"
    video_provider: ProviderName = "stub"

    llm_model: str = "gpt-5.5"
    image_model: str = "gpt-image-1"
    tts_model: str = "gpt-4o-mini-tts"
    video_model: str = "wan2.6-i2v-flash"
    tts_voice: str = "alloy"

    openai_api_key: str | None = None
    openai_base_url: str | None = None

    dashscope_api_key: str | None = None
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str | None = None
    langsmith_endpoint: str | None = None
    langsmith_workspace_id: str | None = None

    artifacts_dir: Path = Path(__file__).resolve().parents[3] / "artifacts"
    ffmpeg_binary: str = "ffmpeg"


def load_settings(
    *,
    env_file: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> Settings:
    effective_environ = dict(environ if environ is not None else os.environ)
    effective_env_file = env_file or Path(__file__).resolve().parents[2] / ".env"
    file_values = _read_dotenv(effective_env_file)

    def pick(name: str, default: str | None = None) -> str | None:
        if name in effective_environ:
            return effective_environ[name]
        return file_values.get(name, default)

    openai_api_key = pick("OPENAI_API_KEY")
    dashscope_api_key = pick("DASHSCOPE_API_KEY")
    ffmpeg_binary = _resolve_ffmpeg_binary(
        configured=pick("FFMPEG_BINARY", "ffmpeg") or "ffmpeg",
        environ=effective_environ,
    )

    repo_root = effective_env_file.parent.parent

    return Settings(
        llm_provider=_pick_provider(
            explicit=pick("LLM_PROVIDER"),
            fallback="openai" if openai_api_key else "qwen" if dashscope_api_key else "stub",
        ),
        image_provider=_pick_provider(
            explicit=pick("IMAGE_PROVIDER"),
            fallback="openai" if openai_api_key else "qwen" if dashscope_api_key else "stub",
        ),
        tts_provider=_pick_provider(
            explicit=pick("TTS_PROVIDER"),
            fallback="openai" if openai_api_key else "qwen" if dashscope_api_key else "stub",
        ),
        video_provider=_pick_provider(
            explicit=pick("VIDEO_PROVIDER"),
            fallback="openai" if openai_api_key else "qwen" if dashscope_api_key else "stub",
        ),
        llm_model=pick("LLM_MODEL", pick("OPENAI_TEXT_MODEL", "gpt-5.5")) or "gpt-5.5",
        image_model=pick("IMAGE_MODEL", pick("OPENAI_IMAGE_MODEL", "gpt-image-1")) or "gpt-image-1",
        tts_model=pick("TTS_MODEL", pick("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")) or "gpt-4o-mini-tts",
        video_model=pick("VIDEO_MODEL", "wan2.6-i2v-flash") or "wan2.6-i2v-flash",
        tts_voice=pick("TTS_VOICE", pick("OPENAI_TTS_VOICE", "alloy")) or "alloy",
        openai_api_key=openai_api_key,
        openai_base_url=pick("OPENAI_BASE_URL"),
        dashscope_api_key=dashscope_api_key,
        dashscope_base_url=pick(
            "DASHSCOPE_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        or "https://dashscope.aliyuncs.com/compatible-mode/v1",
        langsmith_tracing=_as_bool(pick("LANGSMITH_TRACING", "false")),
        langsmith_api_key=pick("LANGSMITH_API_KEY"),
        langsmith_project=pick("LANGSMITH_PROJECT"),
        langsmith_endpoint=pick("LANGSMITH_ENDPOINT"),
        langsmith_workspace_id=pick("LANGSMITH_WORKSPACE_ID"),
        artifacts_dir=_resolve_artifacts_dir(
            configured=pick("ARTIFACTS_DIR", str(repo_root / "artifacts")) or str(repo_root / "artifacts"),
            repo_root=repo_root,
        ),
        ffmpeg_binary=ffmpeg_binary,
    )


def _pick_provider(*, explicit: str | None, fallback: str) -> ProviderName:
    candidate = (explicit or fallback).strip().lower()
    if candidate not in {"stub", "openai", "qwen"}:
        raise ValueError(f"Unsupported provider: {candidate}")
    return candidate  # type: ignore[return-value]


def _read_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def _resolve_ffmpeg_binary(*, configured: str, environ: Mapping[str, str]) -> str:
    candidate = configured.strip()
    if not candidate:
        return "ffmpeg"

    candidate_path = Path(candidate)
    if candidate_path.exists():
        return str(candidate_path)

    if candidate.lower() == "ffmpeg":
        local_appdata = environ.get("LOCALAPPDATA")
        if local_appdata:
            winget_packages_dir = Path(local_appdata) / "Microsoft" / "WinGet" / "Packages"
            if winget_packages_dir.exists():
                matches = sorted(winget_packages_dir.glob("**/ffmpeg.exe"))
                if matches:
                    return str(matches[-1])

    if shutil.which(candidate):
        return candidate

    return candidate


def _resolve_artifacts_dir(*, configured: str, repo_root: Path) -> Path:
    candidate = Path(configured.strip())
    if candidate.is_absolute():
        return candidate
    return (repo_root / candidate).resolve()


def _as_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


settings = load_settings()
