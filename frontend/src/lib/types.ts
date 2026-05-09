export type StageStatus = "pending" | "running" | "completed" | "failed";

export type JobStage = {
  key: string;
  label: string;
  status: StageStatus;
  message?: string;
};

export type JobDetail = {
  jobId: string;
  topic: string;
  style: string;
  status: StageStatus;
  stages: JobStage[];
  previewUrl?: string;
  finalVideoUrl?: string;
};

export type CreateJobInput = {
  topic: string;
  style: string;
};
