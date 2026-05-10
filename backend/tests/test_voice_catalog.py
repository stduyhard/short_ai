from app.core.config import Settings
from app.services.voice_catalog import list_available_voices


def test_list_available_voices_returns_qwen_catalog_for_qwen_tts_model() -> None:
    catalog = list_available_voices(
        Settings(
            tts_provider="qwen",
            tts_model="qwen3-tts-flash",
        )
    )

    assert catalog["provider"] == "qwen"
    assert catalog["model"] == "qwen3-tts-flash"
    assert catalog["voices"] == [
        {"value": "auto", "label": "自动匹配"},
        {"value": "Chelsie", "label": "Chelsie"},
        {"value": "Serena", "label": "Serena"},
        {"value": "Ethan", "label": "Ethan"},
        {"value": "Dylan", "label": "Dylan"},
    ]


def test_list_available_voices_returns_openai_catalog_for_openai_tts_model() -> None:
    catalog = list_available_voices(
        Settings(
            tts_provider="openai",
            tts_model="gpt-4o-mini-tts",
        )
    )

    assert catalog["provider"] == "openai"
    assert catalog["model"] == "gpt-4o-mini-tts"
    assert catalog["voices"] == [
        {"value": "auto", "label": "自动匹配"},
        {"value": "alloy", "label": "alloy"},
        {"value": "ash", "label": "ash"},
        {"value": "sage", "label": "sage"},
        {"value": "verse", "label": "verse"},
    ]


def test_list_available_voices_falls_back_to_default_catalog_for_unknown_model() -> None:
    catalog = list_available_voices(
        Settings(
            tts_provider="stub",
            tts_model="unknown-model",
        )
    )

    assert catalog["provider"] == "stub"
    assert catalog["model"] == "unknown-model"
    assert catalog["voices"][0] == {"value": "auto", "label": "自动匹配"}
