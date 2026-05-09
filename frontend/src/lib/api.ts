import type { JobDetail } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function fetchJobDetail(jobId: string): Promise<JobDetail> {
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch job detail for ${jobId}`);
  }

  return (await response.json()) as JobDetail;
}
