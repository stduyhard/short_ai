from pathlib import Path

from app.providers.tts import StubTTSProvider, TTSRequest


def test_stub_tts_provider_creates_valid_wav_placeholder(tmp_path: Path) -> None:
    provider = StubTTSProvider(tmp_path)

    response = provider.synthesize(
        TTSRequest(
            text="这是一个用于渲染烟雾测试的占位旁白。",
            metadata={"job_id": "stub-job"},
        )
    )

    audio_path = Path(response.asset_uri)

    assert response.provider_name == "stub"
    assert audio_path.exists()
    assert audio_path.suffix == ".wav"
    assert audio_path.read_bytes()[:4] == b"RIFF"
