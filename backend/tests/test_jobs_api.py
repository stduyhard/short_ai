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


def test_get_job_detail_returns_created_job_with_default_stages() -> None:
    create_response = client.post(
        "/api/jobs",
        json={"topic": "番茄工作法", "style": "干货"},
    )

    assert create_response.status_code == 201
    job_id = create_response.json()["job_id"]

    detail_response = client.get(f"/api/jobs/{job_id}")

    assert detail_response.status_code == 200
    assert detail_response.json() == {
        "job_id": job_id,
        "topic": "番茄工作法",
        "style": "干货",
        "status": "pending",
        "stages": [
            {"name": "idea_generation", "status": "pending"},
            {"name": "outline", "status": "pending"},
            {"name": "script", "status": "pending"},
            {"name": "storyboard", "status": "pending"},
            {"name": "voiceover", "status": "pending"},
            {"name": "render", "status": "pending"},
        ],
    }
