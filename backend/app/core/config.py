from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "short-video-backend"
    openai_api_key: str | None = None
    openai_text_model: str = "gpt-5.5"
    openai_image_model: str = "gpt-image-1"
    openai_tts_model: str = "gpt-4o-mini-tts"
    openai_tts_voice: str = "alloy"
    artifacts_dir: Path = Path("artifacts")
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

    return Settings(
        openai_api_key=pick("OPENAI_API_KEY"),
        openai_text_model=pick("OPENAI_TEXT_MODEL", "gpt-5.5") or "gpt-5.5",
        openai_image_model=pick("OPENAI_IMAGE_MODEL", "gpt-image-1") or "gpt-image-1",
        openai_tts_model=pick("OPENAI_TTS_MODEL", "gpt-4o-mini-tts") or "gpt-4o-mini-tts",
        openai_tts_voice=pick("OPENAI_TTS_VOICE", "alloy") or "alloy",
        artifacts_dir=Path(pick("ARTIFACTS_DIR", "artifacts") or "artifacts"),
        ffmpeg_binary=pick("FFMPEG_BINARY", "ffmpeg") or "ffmpeg",
    )


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


settings = load_settings()
