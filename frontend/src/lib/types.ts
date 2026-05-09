export type StageStatus = "pending" | "running" | "completed" | "failed";
export type JobStatus = StageStatus | "degraded";

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
  status: JobStatus;
  stages: JobStage[];
  brief?: string | null;
  script?: string | null;
  storyboard?: Array<{
    shot: string;
    caption: string;
  }> | null;
  visualAssets?: string[] | null;
  voiceAsset?: string | null;
  finalVideo?: string | null;
  errorMessage?: string | null;
  previewUrl?: string;
  finalVideoUrl?: string;
};

export type CreateJobInput = {
  topic: string;
  style: string;
};
