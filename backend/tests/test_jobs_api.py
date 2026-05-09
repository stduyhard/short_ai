from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_job() -> None:
    response = client.post(
        "/api/jobs",
        json={"topic": "时间管理", "style": "励志"},
    )

    assert response.status_code == 201
    assert response.json()["job_id"]
    assert response.json()["topic"] == "时间管理"
    assert response.json()["style"] == "励志"
    assert response.json()["status"] == "pending"
