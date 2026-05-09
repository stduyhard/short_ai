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
        "jobId": job_id,
        "topic": "番茄工作法",
        "style": "干货",
        "status": "pending",
        "stages": [
            {"key": "director", "label": "创意策划", "status": "pending"},
            {"key": "script", "label": "文案生成", "status": "pending"},
            {"key": "storyboard", "label": "分镜生成", "status": "pending"},
            {"key": "visual", "label": "视觉素材生成", "status": "pending"},
            {"key": "voice", "label": "配音与字幕生成", "status": "pending"},
            {"key": "editor", "label": "视频渲染", "status": "pending"},
        ],
        "brief": None,
        "script": None,
        "storyboard": None,
        "visualAssets": None,
        "voiceAsset": None,
        "finalVideo": None,
        "errorMessage": None,
    }


def test_get_job_detail_returns_404_when_job_missing() -> None:
    response = client.get("/api/jobs/missing-job-id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found"}


def test_run_job_executes_workflow_and_updates_job_state() -> None:
    create_response = client.post(
        "/api/jobs",
        json={"topic": "AI 口播", "style": "教程"},
    )

    assert create_response.status_code == 201
    job_id = create_response.json()["job_id"]

    run_response = client.post(f"/api/jobs/{job_id}/run")

    assert run_response.status_code == 202
    assert run_response.json() == {"jobId": job_id, "status": "degraded"}

    detail_response = client.get(f"/api/jobs/{job_id}")

    assert detail_response.status_code == 200
    assert detail_response.json()["status"] == "degraded"
    assert detail_response.json()["stages"] == [
        {"key": "director", "label": "创意策划", "status": "completed"},
        {"key": "script", "label": "文案生成", "status": "completed"},
        {"key": "storyboard", "label": "分镜生成", "status": "completed"},
        {"key": "visual", "label": "视觉素材生成", "status": "completed"},
        {"key": "voice", "label": "配音与字幕生成", "status": "completed"},
        {"key": "editor", "label": "视频渲染", "status": "completed"},
    ]
    assert detail_response.json()["brief"]
    assert detail_response.json()["script"]
    assert detail_response.json()["storyboard"]
    assert detail_response.json()["visualAssets"]
    assert detail_response.json()["voiceAsset"].endswith((".mp3", ".wav"))
    assert detail_response.json()["finalVideo"] == ""
