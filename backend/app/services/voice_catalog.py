from __future__ import annotations

from app.core.config import Settings


DEFAULT_VOICE_OPTIONS = [
    {"value": "auto", "label": "自动匹配"},
    {"value": "Chelsie", "label": "Chelsie"},
    {"value": "Serena", "label": "Serena"},
    {"value": "Ethan", "label": "Ethan"},
    {"value": "Dylan", "label": "Dylan"},
]


def list_available_voices(settings: Settings) -> dict[str, object]:
    return {
        "provider": settings.tts_provider,
        "model": settings.tts_model,
        "voices": DEFAULT_VOICE_OPTIONS,
    }
