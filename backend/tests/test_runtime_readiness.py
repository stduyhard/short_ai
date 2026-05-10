from fastapi.testclient import TestClient

from app.main import app, settings


client = TestClient(app)


def test_runtime_readiness_reports_missing_dependencies(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "qwen")
    monkeypatch.setattr(settings, "image_provider", "qwen")
    monkeypatch.setattr(settings, "tts_provider", "qwen")
    monkeypatch.setattr(settings, "openai_api_key", None)
    monkeypatch.setattr(settings, "dashscope_api_key", None)
    monkeypatch.setattr("app.services.runtime_readiness.shutil.which", lambda _: None)

    response = client.get("/api/runtime/readiness")

    assert response.status_code == 200
    assert response.json() == {
        "providersConfigured": False,
        "ffmpegAvailable": False,
        "readyForRealGeneration": False,
    }


def test_runtime_readiness_reports_provider_configuration(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "qwen")
    monkeypatch.setattr(settings, "image_provider", "qwen")
    monkeypatch.setattr(settings, "tts_provider", "qwen")
    monkeypatch.setattr(settings, "dashscope_api_key", "dash-key")
    monkeypatch.setattr("app.services.runtime_readiness.shutil.which", lambda _: "C:/ffmpeg/bin/ffmpeg.exe")

    response = client.get("/api/runtime/readiness")

    assert response.status_code == 200
    assert response.json() == {
        "providersConfigured": True,
        "ffmpegAvailable": True,
        "readyForRealGeneration": True,
    }
