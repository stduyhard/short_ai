from __future__ import annotations

from app.core.config import Settings
from app.providers.image import ImageProvider, OpenAIImageProvider, QwenImageProvider, StubImageProvider
from app.providers.llm import LLMProvider, OpenAILLMProvider, QwenLLMProvider, StubLLMProvider
from app.providers.storage import StorageProvider
from app.providers.tts import OpenAITTSProvider, QwenTTSProvider, StubTTSProvider, TTSProvider
from app.providers.video import QwenVideoProvider, StubVideoProvider, VideoProvider


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "stub":
        return StubLLMProvider()
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        return OpenAILLMProvider(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            base_url=settings.openai_base_url,
        )
    if settings.llm_provider == "qwen":
        if not settings.dashscope_api_key:
            raise ValueError("DASHSCOPE_API_KEY is required when LLM_PROVIDER=qwen")
        return QwenLLMProvider(
            api_key=settings.dashscope_api_key,
            model=settings.llm_model,
            base_url=settings.dashscope_base_url,
        )
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


def build_image_provider(*, settings: Settings, storage_provider: StorageProvider) -> ImageProvider:
    if settings.image_provider == "stub":
        return StubImageProvider(storage_provider)
    if settings.image_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when IMAGE_PROVIDER=openai")
        return OpenAIImageProvider(
            api_key=settings.openai_api_key,
            model=settings.image_model,
            storage_provider=storage_provider,
        )
    if settings.image_provider == "qwen":
        if not settings.dashscope_api_key:
            raise ValueError("DASHSCOPE_API_KEY is required when IMAGE_PROVIDER=qwen")
        return QwenImageProvider(
            api_key=settings.dashscope_api_key,
            model=settings.image_model,
            base_url=_dashscope_api_base_url(settings.dashscope_base_url),
            storage_provider=storage_provider,
        )
    raise ValueError(f"Unsupported image provider: {settings.image_provider}")


def build_tts_provider(settings: Settings) -> TTSProvider:
    if settings.tts_provider == "stub":
        return StubTTSProvider(settings.artifacts_dir)
    if settings.tts_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when TTS_PROVIDER=openai")
        return OpenAITTSProvider(
            api_key=settings.openai_api_key,
            model=settings.tts_model,
            default_voice=settings.tts_voice,
            output_dir=settings.artifacts_dir,
        )
    if settings.tts_provider == "qwen":
        if not settings.dashscope_api_key:
            raise ValueError("DASHSCOPE_API_KEY is required when TTS_PROVIDER=qwen")
        return QwenTTSProvider(
            api_key=settings.dashscope_api_key,
            model=settings.tts_model,
            default_voice=settings.tts_voice,
            output_dir=settings.artifacts_dir,
            base_url=_dashscope_api_base_url(settings.dashscope_base_url),
        )
    raise ValueError(f"Unsupported TTS provider: {settings.tts_provider}")


def build_video_provider(*, settings: Settings, storage_provider: StorageProvider) -> VideoProvider:
    if settings.video_provider == "stub":
        return StubVideoProvider(storage_provider)
    if settings.video_provider == "openai":
        raise ValueError("OpenAI video provider is not implemented")
    if settings.video_provider == "qwen":
        if not settings.dashscope_api_key:
            raise ValueError("DASHSCOPE_API_KEY is required when VIDEO_PROVIDER=qwen")
        return QwenVideoProvider(
            api_key=settings.dashscope_api_key,
            model=settings.video_model,
            base_url=_dashscope_api_base_url(settings.dashscope_base_url),
            storage_provider=storage_provider,
        )
    raise ValueError(f"Unsupported video provider: {settings.video_provider}")


def _dashscope_api_base_url(compatible_base_url: str) -> str:
    return compatible_base_url.replace("/compatible-mode/v1", "/api/v1")
