import type { CreateJobInput, JobDetail } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

type CreateJobResponse = {
  job_id: string;
  topic: string;
  style: string;
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
    throw new Error("Failed to create job");
  }

  return (await response.json()) as CreateJobResponse;
}

export async function fetchJobDetail(jobId: string): Promise<JobDetail> {
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch job detail for ${jobId}`);
  }

  return (await response.json()) as JobDetail;
}
