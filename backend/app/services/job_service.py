from uuid import uuid4

from app.core.models import CreateJobRequest, JobDetailResponse, JobResponse, JobStageResponse


DEFAULT_STAGES = [
    {"key": "director", "label": "创意策划"},
    {"key": "script", "label": "文案生成"},
    {"key": "storyboard", "label": "分镜生成"},
    {"key": "visual", "label": "视觉素材生成"},
    {"key": "voice", "label": "配音与字幕生成"},
    {"key": "editor", "label": "视频渲染"},
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
