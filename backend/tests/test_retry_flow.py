from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_retry_job_stage_returns_accepted_stage() -> None:
    create_response = client.post(
        "/api/jobs",
        json={"topic": "短视频增长", "style": "分析"},
    )

    assert create_response.status_code == 201
    job_id = create_response.json()["job_id"]

    retry_response = client.post(
        f"/api/jobs/{job_id}/retry",
        json={"stage": "script"},
    )

    assert retry_response.status_code == 202
    assert retry_response.json() == {
        "jobId": job_id,
        "stage": "script",
        "status": "accepted",
    }
