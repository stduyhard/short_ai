from __future__ import annotations


VOICE_ALIASES = {
    "Serena": "Seren",
}


STYLE_VOICE_MAP = {
    "治愈": "Seren",
    "励志": "Ethan",
    "干货": "Chelsie",
    "教程": "Chelsie",
    "分析": "Dylan",
    "轻松": "Seren",
}


def resolve_voice_selection(*, style: str, voice_selection: str, default_voice: str) -> str:
    normalized_voice = _normalize_voice(voice_selection)
    if normalized_voice and normalized_voice != "auto":
        return normalized_voice

    for keyword, mapped_voice in STYLE_VOICE_MAP.items():
        if keyword in style:
            return mapped_voice

    return _normalize_voice(default_voice)


def _normalize_voice(voice: str) -> str:
    cleaned = voice.strip()
    return VOICE_ALIASES.get(cleaned, cleaned)
