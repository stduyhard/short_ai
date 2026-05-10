from pathlib import Path

from app.core.config import Settings
from app.providers.factory import build_image_provider, build_llm_provider, build_tts_provider
from app.providers.storage import LocalStorageProvider


def test_provider_factory_builds_qwen_implementations() -> None:
    settings = Settings(
        llm_provider="qwen",
        image_provider="qwen",
        tts_provider="qwen",
        llm_model="qwen-plus-latest",
        image_model="qwen-image-2.0",
        tts_model="qwen3-tts-flash",
        dashscope_api_key="dash-key",
    )
    storage = LocalStorageProvider(Path("artifacts"))

    llm_provider = build_llm_provider(settings)
    image_provider = build_image_provider(settings=settings, storage_provider=storage)
    tts_provider = build_tts_provider(settings)

    assert llm_provider.provider_name == "qwen"
    assert image_provider.provider_name == "qwen"
    assert tts_provider.provider_name == "qwen"


def test_provider_factory_falls_back_to_stub_when_configured() -> None:
    settings = Settings()
    storage = LocalStorageProvider(Path("artifacts"))

    assert build_llm_provider(settings).provider_name == "stub"
    assert build_image_provider(settings=settings, storage_provider=storage).provider_name == "stub"
    assert build_tts_provider(settings).provider_name == "stub"
