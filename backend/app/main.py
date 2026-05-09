from uuid import uuid4

from fastapi import FastAPI

from .core.config import settings
from .core.models import CreateJobRequest, JobResponse


app = FastAPI(title=settings.app_name)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/jobs", response_model=JobResponse, status_code=201)
def create_job(payload: CreateJobRequest) -> JobResponse:
    return JobResponse(
        job_id=str(uuid4()),
        topic=payload.topic,
        style=payload.style,
        status="pending",
    )
