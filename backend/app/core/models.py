from pydantic import BaseModel


class CreateJobRequest(BaseModel):
    topic: str
    style: str


class JobResponse(BaseModel):
    job_id: str
    topic: str
    style: str
    status: str
