from __future__ import annotations

from collections.abc import Sequence

from app.core.config import Settings


VoiceOption = dict[str, str]

DEFAULT_VOICE_OPTIONS: list[VoiceOption] = [
    {"value": "auto", "label": "自动匹配"},
    {"value": "Chelsie", "label": "Chelsie"},
    {"value": "Seren", "label": "Seren"},
    {"value": "Ethan", "label": "Ethan"},
    {"value": "Dylan", "label": "Dylan"},
]

VOICE_CATALOGS: dict[tuple[str, str], list[VoiceOption]] = {
    (
        "qwen",
        "qwen3-tts-flash",
    ): [
        {"value": "auto", "label": "自动匹配"},
        {"value": "Chelsie", "label": "Chelsie"},
        {"value": "Seren", "label": "Seren"},
        {"value": "Ethan", "label": "Ethan"},
        {"value": "Dylan", "label": "Dylan"},
    ],
    (
        "openai",
        "gpt-4o-mini-tts",
    ): [
        {"value": "auto", "label": "自动匹配"},
        {"value": "alloy", "label": "alloy"},
        {"value": "ash", "label": "ash"},
        {"value": "sage", "label": "sage"},
        {"value": "verse", "label": "verse"},
    ],
}


def list_available_voices(settings: Settings) -> dict[str, object]:
    voices = _resolve_voice_options(settings.tts_provider, settings.tts_model)
    return {
        "provider": settings.tts_provider,
        "model": settings.tts_model,
        "voices": voices,
    }


def _resolve_voice_options(provider: str, model: str) -> Sequence[VoiceOption]:
    return VOICE_CATALOGS.get((provider, model), DEFAULT_VOICE_OPTIONS)
