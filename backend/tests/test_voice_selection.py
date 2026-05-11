from app.services.voice_selection import resolve_voice_selection


def test_resolve_voice_selection_prefers_explicit_voice() -> None:
    assert resolve_voice_selection(style="治愈", voice_selection="Chelsie", default_voice="DefaultVoice") == "Chelsie"


def test_resolve_voice_selection_uses_style_mapping_for_auto() -> None:
    assert resolve_voice_selection(style="治愈", voice_selection="auto", default_voice="DefaultVoice") == "Seren"


def test_resolve_voice_selection_normalizes_legacy_alias() -> None:
    assert resolve_voice_selection(style="未知风格", voice_selection="Serena", default_voice="DefaultVoice") == "Seren"


def test_resolve_voice_selection_falls_back_to_default_voice() -> None:
    assert (
        resolve_voice_selection(style="未知风格", voice_selection="auto", default_voice="DefaultVoice")
        == "DefaultVoice"
    )
