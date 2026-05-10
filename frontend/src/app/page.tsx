"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { JobForm } from "../components/job-form";
import { createJob, fetchVoiceOptions } from "../lib/api";
import type { CreateJobInput, VoiceOption } from "../lib/types";

export default function HomePage() {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [voiceOptions, setVoiceOptions] = useState<VoiceOption[] | undefined>(undefined);

  useEffect(() => {
    let active = true;

    async function loadVoiceOptions() {
      try {
        const options = await fetchVoiceOptions();
        if (active) {
          setVoiceOptions(options);
        }
      } catch {
        if (active) {
          setVoiceOptions(undefined);
        }
      }
    }

    void loadVoiceOptions();

    return () => {
      active = false;
    };
  }, []);

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
      <JobForm onSubmit={handleSubmit} voiceOptions={voiceOptions} />
      {submitError ? <p role="alert">{submitError}</p> : null}
    </main>
  );
}
