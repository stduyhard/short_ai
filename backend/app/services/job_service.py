from datetime import datetime, timezone
from typing import cast
from uuid import uuid4

from app.core.config import settings
from app.core.models import CreateJobRequest, JobDetailResponse, JobResponse, JobStageResponse, RecentJobResponse
from app.observability.langsmith import maybe_traceable, maybe_tracing_context
from app.workflows.graph import build_graph
from app.workflows.state import WorkflowState


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
            createdAt=datetime.now(timezone.utc).isoformat(),
            voiceSelection=payload.voice,
            duration=payload.duration,
            shotCount=payload.shotCount,
            subtitlesEnabled=payload.subtitlesEnabled,
            aspectRatio="9:16",
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
            voice=job.voiceSelection,
            duration=job.duration,
            shotCount=job.shotCount,
            subtitlesEnabled=job.subtitlesEnabled,
            aspectRatio=job.aspectRatio,
            status=job.status,
        )

    def get_job(self, job_id: str) -> JobDetailResponse | None:
        return self._jobs.get(job_id)

    def list_recent_jobs(self, *, limit: int = 10) -> list[RecentJobResponse]:
        jobs = list(self._jobs.values())
        jobs.sort(key=lambda job: job.createdAt or "", reverse=True)
        return [
            RecentJobResponse(
                jobId=job.jobId,
                topic=job.topic,
                style=job.style,
                status=job.status,
                createdAt=job.createdAt or "",
            )
            for job in jobs[:limit]
        ]

    def run_job(self, job_id: str) -> JobDetailResponse | None:
        job = self._jobs.get(job_id)
        if job is None:
            return None

        job.status = "running"
        for stage in job.stages:
            stage.status = "pending"

        try:
            with maybe_tracing_context(settings, project_name=settings.langsmith_project):
                workflow_result = self._invoke_workflow_with_tracing(job)
        except Exception as exc:
            job.status = "failed"
            job.errorMessage = str(exc)
            return job
        completed_stages = set(workflow_result.get("stages", []))

        for stage in job.stages:
            stage.status = "completed" if stage.key in completed_stages else "pending"

        job.status = workflow_result.get("final_status", "completed")
        job.brief = workflow_result.get("brief")
        job.script = workflow_result.get("script")
        job.storyboard = workflow_result.get("storyboard")
        job.visualAssets = workflow_result.get("visual_assets")
        job.videoSegments = workflow_result.get("video_segments")
        job.voiceAsset = workflow_result.get("voice_asset")
        job.finalVideo = workflow_result.get("final_video")
        job.duration = workflow_result.get("duration", job.duration)
        job.shotCount = workflow_result.get("shot_count", job.shotCount)
        job.subtitlesEnabled = workflow_result.get("subtitles_enabled", job.subtitlesEnabled)
        job.aspectRatio = workflow_result.get("aspect_ratio", job.aspectRatio)
        job.errorMessage = None
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

    @maybe_traceable(settings, name="generate-video-job", run_type="chain")
    def _invoke_workflow_with_tracing(self, job: JobDetailResponse) -> WorkflowState:
        return cast(
            WorkflowState,
            self._workflow.invoke(
            {
                "job_id": job.jobId,
                "topic": job.topic,
                "style": job.style,
                "voice_selection": job.voiceSelection,
                "duration": job.duration,
                "shot_count": job.shotCount,
                "subtitles_enabled": job.subtitlesEnabled,
                "aspect_ratio": job.aspectRatio,
                "stages": [],
                "brief": "",
                "script": "",
                "storyboard": [],
                "visual_assets": [],
                "video_segments": [],
                "segment_duration_seconds": 0.0,
                "voice_asset": "",
                "final_video": "",
                "final_status": "running",
            }
            ),
        )
