"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { GenerationControls } from "../components/generation-controls";
import { JobForm } from "../components/job-form";
import { RuntimePanel } from "../components/runtime-panel";
import { createJob, fetchVoiceCatalog } from "../lib/api";
import type { CreateJobInput, VoiceCatalog } from "../lib/types";

export default function HomePage() {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [voiceCatalog, setVoiceCatalog] = useState<VoiceCatalog | null>(null);
  const [duration, setDuration] = useState<15 | 30 | 60>(30);
  const [shotCount, setShotCount] = useState<3 | 5 | 7>(5);
  const [subtitlesEnabled, setSubtitlesEnabled] = useState(true);

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
      const job = await createJob({
        ...value,
        duration,
        shotCount,
        subtitlesEnabled,
      });
      router.push(`/jobs/${job.job_id}`);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "提交任务失败");
    }
  }

  return (
    <main className="workbench-shell">
      <section className="workbench-hero">
        <div className="hero-copy">
          <p className="hero-kicker">Pixelle-style Studio</p>
          <h1>AI 短视频工作台</h1>
          <p className="hero-description">
            输入主题与风格，配置核心参数后，系统会按真实工作流生成中文短视频。
          </p>
        </div>
        <JobForm
          duration={duration}
          onSubmit={handleSubmit}
          shotCount={shotCount}
          subtitlesEnabled={subtitlesEnabled}
          voiceOptions={voiceCatalog?.voices}
        />
        {submitError ? <p className="error-banner" role="alert">{submitError}</p> : null}
      </section>
      <GenerationControls
        duration={duration}
        onDurationChange={setDuration}
        onShotCountChange={setShotCount}
        onSubtitlesEnabledChange={setSubtitlesEnabled}
        shotCount={shotCount}
        subtitlesEnabled={subtitlesEnabled}
      />
      <RuntimePanel voiceCatalog={voiceCatalog} />
    </main>
  );
}
