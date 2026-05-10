from __future__ import annotations


STYLE_VOICE_MAP = {
    "治愈": "Serena",
    "励志": "Ethan",
    "干货": "Chelsie",
    "教程": "Chelsie",
    "分析": "Dylan",
    "轻松": "Serena",
}


def resolve_voice_selection(*, style: str, voice_selection: str, default_voice: str) -> str:
    normalized_voice = voice_selection.strip()
    if normalized_voice and normalized_voice != "auto":
        return normalized_voice

    for keyword, mapped_voice in STYLE_VOICE_MAP.items():
        if keyword in style:
            return mapped_voice

    return default_voice
