from uuid import uuid4

from app.core.models import CreateJobRequest, JobDetailResponse, JobResponse, JobStageResponse
from app.workflows.graph import build_graph


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
        self._workflow = build_graph()

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

    def run_job(self, job_id: str) -> JobDetailResponse | None:
        job = self._jobs.get(job_id)
        if job is None:
            return None

        job.status = "running"
        for stage in job.stages:
            stage.status = "pending"

        workflow_result = self._workflow.invoke(
            {
                "topic": job.topic,
                "style": job.style,
                "stages": [],
                "brief": "",
                "script": "",
                "storyboard": [],
                "visual_assets": [],
                "voice_asset": "",
                "final_video": "",
                "final_status": "running",
            }
        )
        completed_stages = set(workflow_result.get("stages", []))

        for stage in job.stages:
            stage.status = "completed" if stage.key in completed_stages else "pending"

        job.status = workflow_result.get("final_status", "completed")
        return job

    def retry_stage(self, job_id: str, stage_key: str) -> dict[str, str] | None:
        job = self._jobs.get(job_id)
        if job is None:
            return None

        if not any(stage.key == stage_key for stage in job.stages):
            raise ValueError(f"Unknown stage: {stage_key}")

        return {
            "jobId": job.jobId,
            "stage": stage_key,
            "status": "accepted",
        }
