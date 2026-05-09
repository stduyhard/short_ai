from pydantic import BaseModel


class CreateJobRequest(BaseModel):
    topic: str
    style: str


class JobResponse(BaseModel):
    job_id: str
    topic: str
    style: str
    status: str


class JobStageResponse(BaseModel):
    key: str
    label: str
    status: str


class JobDetailResponse(BaseModel):
    jobId: str
    topic: str
    style: str
    status: str
    stages: list[JobStageResponse]
    brief: str | None = None
    script: str | None = None
    storyboard: list[dict[str, str]] | None = None
    visualAssets: list[str] | None = None
    voiceAsset: str | None = None
    finalVideo: str | None = None
    errorMessage: str | None = None
