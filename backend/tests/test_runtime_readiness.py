from fastapi.testclient import TestClient

from app.main import app, settings


client = TestClient(app)


def test_runtime_readiness_reports_missing_dependencies(monkeypatch) -> None:
    monkeypatch.setattr(settings, "openai_api_key", None)
    monkeypatch.setattr("app.services.runtime_readiness.shutil.which", lambda _: None)

    response = client.get("/api/runtime/readiness")

    assert response.status_code == 200
    assert response.json() == {
        "openaiConfigured": False,
        "ffmpegAvailable": False,
        "readyForRealGeneration": False,
    }
