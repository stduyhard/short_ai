from fastapi import FastAPI, HTTPException

from app.core.config import settings
from app.core.models import CreateJobRequest, JobDetailResponse, JobResponse
from app.services.job_service import JobService


app = FastAPI(title=settings.app_name)
job_service = JobService()


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/jobs", response_model=JobResponse, status_code=201)
def create_job(payload: CreateJobRequest) -> JobResponse:
    return job_service.create_job(payload)


@app.get("/api/jobs/{job_id}", response_model=JobDetailResponse)
def get_job(job_id: str) -> JobDetailResponse:
    job = job_service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
