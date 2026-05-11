from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_langsmith_runtime_endpoint_returns_safe_runtime_flags() -> None:
    response = client.get("/api/runtime/langsmith")

    assert response.status_code == 200
    payload = response.json()

    assert "tracingEnabled" in payload
    assert "apiKeyConfigured" in payload
    assert "moduleImportable" in payload
    assert "pythonExecutable" in payload
    assert "pid" in payload
    assert "cwd" in payload
    assert "langsmith_api_key" not in payload
