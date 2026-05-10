from typing import Literal

from pydantic import BaseModel


class CreateJobRequest(BaseModel):
    topic: str
    style: str
    voice: str = "auto"
    duration: Literal[15, 30, 60] = 30
    shotCount: Literal[3, 5, 7] = 5
    subtitlesEnabled: bool = True


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


class JobDetailResponse(BaseModel):
    jobId: str
    topic: str
    style: str
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
    voiceAsset: str | None = None
    finalVideo: str | None = None
    errorMessage: str | None = None
