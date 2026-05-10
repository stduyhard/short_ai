from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.core.config import settings
from app.core.models import CreateJobRequest, JobDetailResponse, JobResponse
from app.services.job_service import JobService
from app.services.runtime_readiness import inspect_runtime_readiness


app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/artifacts", StaticFiles(directory=settings.artifacts_dir), name="artifacts")
job_service = JobService()


class JobRunResponse(BaseModel):
    jobId: str
    status: str


class JobRetryRequest(BaseModel):
    stage: str


class JobRetryResponse(BaseModel):
    jobId: str
    stage: str
    status: str


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/runtime/readiness")
def get_runtime_readiness() -> dict[str, bool]:
    return inspect_runtime_readiness(settings).to_response()


@app.post("/api/jobs", response_model=JobResponse, status_code=201)
def create_job(payload: CreateJobRequest) -> JobResponse:
    return job_service.create_job(payload)


@app.get("/api/jobs/{job_id}", response_model=JobDetailResponse)
def get_job(job_id: str) -> JobDetailResponse:
    job = job_service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/api/jobs/{job_id}/run", response_model=JobRunResponse, status_code=202)
def run_job(job_id: str) -> JobRunResponse:
    job = job_service.run_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobRunResponse(jobId=job.jobId, status=job.status)


@app.post("/api/jobs/{job_id}/retry", response_model=JobRetryResponse, status_code=202)
def retry_job(job_id: str, payload: JobRetryRequest) -> JobRetryResponse:
    try:
        result = job_service.retry_stage(job_id, payload.stage)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobRetryResponse(**result)
