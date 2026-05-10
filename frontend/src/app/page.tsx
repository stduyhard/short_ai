"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { JobForm } from "../components/job-form";
import { createJob, fetchVoiceCatalog } from "../lib/api";
import type { CreateJobInput, VoiceCatalog } from "../lib/types";

export default function HomePage() {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [voiceCatalog, setVoiceCatalog] = useState<VoiceCatalog | null>(null);

  useEffect(() => {
    let active = true;

    async function loadVoiceCatalog() {
      try {
        const catalog = await fetchVoiceCatalog();
        if (active) {
          setVoiceCatalog(catalog);
        }
      } catch {
        if (active) {
          setVoiceCatalog(null);
        }
      }
    }

    void loadVoiceCatalog();

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
      {voiceCatalog ? <p>当前音色目录：{voiceCatalog.provider} / {voiceCatalog.model}</p> : null}
      <JobForm onSubmit={handleSubmit} voiceOptions={voiceCatalog?.voices} />
      {submitError ? <p role="alert">{submitError}</p> : null}
    </main>
  );
}
