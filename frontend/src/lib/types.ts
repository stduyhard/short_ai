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
  createdAt?: string | null;
  voiceSelection: string;
  duration: number;
  shotCount: number;
  subtitlesEnabled: boolean;
  aspectRatio: string;
  status: JobStatus;
  stages: JobStage[];
  brief?: string | null;
  script?: string | null;
  storyboard?: Array<{
    shot: string;
    caption: string;
  }> | null;
  visualAssets?: string[] | null;
  videoSegments?: string[] | null;
  voiceAsset?: string | null;
  finalVideo?: string | null;
  errorMessage?: string | null;
  previewUrl?: string;
  finalVideoUrl?: string;
};

export type RecentJob = {
  jobId: string;
  topic: string;
  style: string;
  status: JobStatus;
  createdAt: string;
};

export type CreateJobInput = {
  topic: string;
  style: string;
  voice: string;
  duration: 15 | 30 | 60;
  shotCount: 3 | 5 | 7;
  subtitlesEnabled: boolean;
};

export type VoiceOption = {
  value: string;
  label: string;
};

export type VoiceCatalog = {
  provider: string;
  model: string;
  voices: VoiceOption[];
};

export type RuntimeReadiness = {
  providersConfigured: boolean;
  ffmpegAvailable: boolean;
  readyForRealGeneration: boolean;
};
