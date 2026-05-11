import type {
  CreateJobInput,
  JobDetail,
  RecentJob,
  RuntimeReadiness,
  VoiceCatalog,
  VoiceOption,
} from "./types";

export function resolveApiBaseUrl(rawBaseUrl?: string): string {
  const normalized = (rawBaseUrl ?? "http://127.0.0.1:8001").trim();
  return normalized.replace(/\/+$/, "") || "http://127.0.0.1:8001";
}

const API_BASE_URL = resolveApiBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL);

type CreateJobResponse = {
  job_id: string;
  topic: string;
  style: string;
  status: string;
};

type RunJobResponse = {
  jobId: string;
  status: string;
};

export async function createJob(input: CreateJobInput): Promise<CreateJobResponse> {
  const response = await fetch(`${API_BASE_URL}/api/jobs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to create job"));
  }

  return (await response.json()) as CreateJobResponse;
}

export async function runJob(jobId: string): Promise<RunJobResponse> {
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}/run`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, `Failed to run job ${jobId}`));
  }

  return (await response.json()) as RunJobResponse;
}

export async function fetchJobDetail(jobId: string): Promise<JobDetail> {
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, `Failed to fetch job detail for ${jobId}`));
  }

  return (await response.json()) as JobDetail;
}

export async function fetchRecentJobs(): Promise<RecentJob[]> {
  const response = await fetch(`${API_BASE_URL}/api/jobs`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to fetch recent jobs"));
  }

  return (await response.json()) as RecentJob[];
}

export async function fetchVoiceCatalog(): Promise<VoiceCatalog> {
  const response = await fetch(`${API_BASE_URL}/api/voices`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to fetch voice options"));
  }

  return (await response.json()) as VoiceCatalog;
}

export async function fetchRuntimeReadiness(): Promise<RuntimeReadiness> {
  const response = await fetch(`${API_BASE_URL}/api/runtime/readiness`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to fetch runtime readiness"));
  }

  return (await response.json()) as RuntimeReadiness;
}

export async function fetchVoiceOptions(): Promise<VoiceOption[]> {
  return (await fetchVoiceCatalog()).voices;
}

export function toPublicArtifactUrl(assetPath: string, apiBaseUrl: string = API_BASE_URL): string | null {
  if (!assetPath) {
    return null;
  }

  const normalizedBaseUrl = resolveApiBaseUrl(apiBaseUrl);
  const normalized = assetPath.replaceAll("\\", "/");
  const marker = "/artifacts/";
  const markerIndex = normalized.lastIndexOf(marker);

  if (normalized.startsWith("artifacts/")) {
    return `${normalizedBaseUrl}/${normalized}`;
  }

  if (markerIndex >= 0) {
    return `${normalizedBaseUrl}${normalized.slice(markerIndex)}`;
  }

  if (/^https?:\/\//.test(normalized)) {
    return normalized;
  }

  return null;
}

async function readErrorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const payload = (await response.json()) as
      | { detail?: string | Array<{ msg?: string; loc?: Array<string | number> }> }
      | undefined;

    if (typeof payload?.detail === "string" && payload.detail) {
      return payload.detail;
    }

    if (Array.isArray(payload?.detail) && payload.detail.length > 0) {
      const firstError = payload.detail[0];
      const fieldName = typeof firstError?.loc?.[1] === "string" ? firstError.loc[1] : "field";
      const message = firstError?.msg ?? fallback;
      return `${fieldName} ${message}`;
    }
  } catch {}

  return fallback;
}
