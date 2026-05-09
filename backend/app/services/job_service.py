from uuid import uuid4

from app.core.models import CreateJobRequest, JobDetailResponse, JobResponse, JobStageResponse


DEFAULT_STAGES = [
    {"key": "director", "label": "Director"},
    {"key": "script", "label": "Script"},
    {"key": "storyboard", "label": "Storyboard"},
    {"key": "visual", "label": "Visual"},
    {"key": "voice", "label": "Voice"},
    {"key": "editor", "label": "Editor"},
]


class JobService:
    def __init__(self) -> None:
        self._jobs: dict[str, JobDetailResponse] = {}

    def create_job(self, payload: CreateJobRequest) -> JobResponse:
        job_id = str(uuid4())
        job = JobDetailResponse(
            jobId=job_id,
            topic=payload.topic,
            style=payload.style,
            status="pending",
            stages=[
                JobStageResponse(
                    key=stage["key"],
                    label=stage["label"],
                    status="pending",
                )
                for stage in DEFAULT_STAGES
            ],
        )
        self._jobs[job_id] = job
        return JobResponse(
            job_id=job.jobId,
            topic=job.topic,
            style=job.style,
            status=job.status,
        )

    def get_job(self, job_id: str) -> JobDetailResponse | None:
        return self._jobs.get(job_id)
