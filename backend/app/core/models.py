from typing import Literal

from pydantic import BaseModel, field_validator


class CreateJobRequest(BaseModel):
    topic: str
    style: str
    voice: str = "auto"
    duration: Literal[15, 30, 60] = 30
    shotCount: Literal[3, 5, 7] = 5
    subtitlesEnabled: bool = True

    @field_validator("topic", "style")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("is required")
        return normalized


class JobResponse(BaseModel):
    job_id: str
    topic: str
    style: str
    voice: str
    duration: int
    shotCount: int
    subtitlesEnabled: bool
    aspectRatio: str
    status: str


class JobStageResponse(BaseModel):
    key: str
    label: str
    status: str


class RecentJobResponse(BaseModel):
    jobId: str
    topic: str
    style: str
    status: str
    createdAt: str


class JobDetailResponse(BaseModel):
    jobId: str
    topic: str
    style: str
    createdAt: str | None = None
    voiceSelection: str = "auto"
    duration: int = 30
    shotCount: int = 5
    subtitlesEnabled: bool = True
    aspectRatio: str = "9:16"
    status: str
    stages: list[JobStageResponse]
    brief: str | None = None
    script: str | None = None
    storyboard: list[dict[str, str]] | None = None
    visualAssets: list[str] | None = None
    videoSegments: list[str] | None = None
    voiceAsset: str | None = None
    finalVideo: str | None = None
    errorMessage: str | None = None
