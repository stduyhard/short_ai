from uuid import uuid4

from app.core.models import CreateJobRequest, JobDetailResponse, JobResponse, JobStageResponse


DEFAULT_STAGE_NAMES = [
    "idea_generation",
    "outline",
    "script",
    "storyboard",
    "voiceover",
    "render",
]


class JobService:
    def __init__(self) -> None:
        self._jobs: dict[str, JobDetailResponse] = {}

    def create_job(self, payload: CreateJobRequest) -> JobResponse:
        job_id = str(uuid4())
        job = JobDetailResponse(
            job_id=job_id,
            topic=payload.topic,
            style=payload.style,
            status="pending",
            stages=[
                JobStageResponse(name=stage_name, status="pending")
                for stage_name in DEFAULT_STAGE_NAMES
            ],
        )
        self._jobs[job_id] = job
        return JobResponse(
            job_id=job.job_id,
            topic=job.topic,
            style=job.style,
            status=job.status,
        )

    def get_job(self, job_id: str) -> JobDetailResponse | None:
        return self._jobs.get(job_id)
