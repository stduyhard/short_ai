import os
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "short-video-backend"
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_text_model: str = os.getenv("OPENAI_TEXT_MODEL", "gpt-5.5")
    openai_image_model: str = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
    openai_tts_model: str = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
    openai_tts_voice: str = os.getenv("OPENAI_TTS_VOICE", "alloy")
    artifacts_dir: Path = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))
    ffmpeg_binary: str = os.getenv("FFMPEG_BINARY", "ffmpeg")


settings = Settings()
