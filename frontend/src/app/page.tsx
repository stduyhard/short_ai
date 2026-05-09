"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { JobForm } from "../components/job-form";
import { createJob } from "../lib/api";
import type { CreateJobInput } from "../lib/types";

export default function HomePage() {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);

  async function handleSubmit(value: CreateJobInput) {
    setSubmitError(null);

    try {
      const job = await createJob(value);
      router.push(`/jobs/${job.job_id}`);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "提交任务失败");
    }
  }

  return (
    <main>
      <h1>AI 短视频生成</h1>
      <JobForm onSubmit={handleSubmit} />
      {submitError ? <p role="alert">{submitError}</p> : null}
    </main>
  );
}
