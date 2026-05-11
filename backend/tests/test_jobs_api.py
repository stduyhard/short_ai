from fastapi.testclient import TestClient
import pytest

import app.main as main_module
from app.main import app
from app.services.job_service import JobService


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_job_service() -> None:
    original_settings = {
        "llm_provider": main_module.settings.llm_provider,
        "image_provider": main_module.settings.image_provider,
        "tts_provider": main_module.settings.tts_provider,
        "video_provider": main_module.settings.video_provider,
        "dashscope_api_key": main_module.settings.dashscope_api_key,
        "openai_api_key": main_module.settings.openai_api_key,
    }
    main_module.settings.llm_provider = "stub"
    main_module.settings.image_provider = "stub"
    main_module.settings.tts_provider = "stub"
    main_module.settings.video_provider = "stub"
    main_module.settings.dashscope_api_key = None
    main_module.settings.openai_api_key = None
    main_module.job_service = JobService()
    yield
    main_module.settings.llm_provider = original_settings["llm_provider"]
    main_module.settings.image_provider = original_settings["image_provider"]
    main_module.settings.tts_provider = original_settings["tts_provider"]
    main_module.settings.video_provider = original_settings["video_provider"]
    main_module.settings.dashscope_api_key = original_settings["dashscope_api_key"]
    main_module.settings.openai_api_key = original_settings["openai_api_key"]
    main_module.job_service = JobService()


def test_healthcheck() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_available_voices() -> None:
    response = client.get("/api/voices")

    assert response.status_code == 200
    assert response.json() == {
        "provider": "stub",
        "model": "qwen3-tts-flash",
        "voices": [
            {"value": "auto", "label": "自动匹配"},
            {"value": "Chelsie", "label": "Chelsie"},
            {"value": "Seren", "label": "Seren"},
            {"value": "Ethan", "label": "Ethan"},
            {"value": "Dylan", "label": "Dylan"},
        ],
    }


def test_create_job() -> None:
    response = client.post(
        "/api/jobs",
        json={"topic": "时间管理", "style": "励志", "voice": "Chelsie"},
    )

    assert response.status_code == 201
    assert response.json()["job_id"]
    assert response.json()["topic"] == "时间管理"
    assert response.json()["style"] == "励志"
    assert response.json()["voice"] == "Chelsie"
    assert response.json()["status"] == "pending"


def test_create_job_rejects_blank_topic_or_style() -> None:
    response = client.post(
        "/api/jobs",
        json={"topic": "   ", "style": ""},
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_job_persists_generation_controls() -> None:
    response = client.post(
        "/api/jobs",
        json={
            "topic": "时间管理",
            "style": "励志",
            "voice": "Chelsie",
            "duration": 60,
            "shotCount": 7,
            "subtitlesEnabled": False,
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "pending"

    job_id = response.json()["job_id"]
    detail_response = client.get(f"/api/jobs/{job_id}")

    assert detail_response.status_code == 200
    assert detail_response.json()["duration"] == 60
    assert detail_response.json()["shotCount"] == 7
    assert detail_response.json()["subtitlesEnabled"] is False
    assert detail_response.json()["aspectRatio"] == "9:16"
    assert detail_response.json()["voiceSelection"] == "Chelsie"


def test_get_job_detail_returns_created_job_with_default_stages() -> None:
    create_response = client.post(
        "/api/jobs",
        json={"topic": "番茄工作法", "style": "干货"},
    )

    assert create_response.status_code == 201
    job_id = create_response.json()["job_id"]

    detail_response = client.get(f"/api/jobs/{job_id}")

    assert detail_response.status_code == 200
    payload = detail_response.json()
    assert payload["createdAt"]
    assert payload == {
        "jobId": job_id,
        "topic": "番茄工作法",
        "style": "干货",
        "createdAt": payload["createdAt"],
        "duration": 30,
        "shotCount": 5,
        "subtitlesEnabled": True,
        "aspectRatio": "9:16",
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
        "videoSegments": None,
        "voiceAsset": None,
        "finalVideo": None,
        "errorMessage": None,
        "voiceSelection": "auto",
    }


def test_get_job_detail_returns_404_when_job_missing() -> None:
    response = client.get("/api/jobs/missing-job-id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found"}


def test_run_job_executes_workflow_and_updates_job_state() -> None:
    create_response = client.post(
        "/api/jobs",
        json={"topic": "AI 口播", "style": "教程", "voice": "Chelsie"},
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
    assert detail_response.json()["videoSegments"]
    assert detail_response.json()["voiceAsset"].endswith((".mp3", ".wav"))
    assert detail_response.json()["finalVideo"] == ""
    assert detail_response.json()["voiceSelection"] == "Chelsie"


def test_list_recent_jobs_returns_latest_jobs_first() -> None:
    first = client.post("/api/jobs", json={"topic": "第一个任务", "style": "纪实"}).json()
    second = client.post("/api/jobs", json={"topic": "第二个任务", "style": "教程"}).json()

    response = client.get("/api/jobs")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["jobId"] == second["job_id"]
    assert payload[0]["topic"] == "第二个任务"
    assert payload[1]["jobId"] == first["job_id"]
    assert payload[0]["createdAt"]
