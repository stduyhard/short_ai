"use client";

import React, { useEffect, useState } from "react";
import { CurrentJobPanel } from "../components/current-job-panel";
import { GenerationControls } from "../components/generation-controls";
import { JobForm } from "../components/job-form";
import { RecentJobsPanel } from "../components/recent-jobs-panel";
import { RuntimePanel } from "../components/runtime-panel";
import {
  createJob,
  fetchJobDetail,
  fetchRecentJobs,
  fetchRuntimeReadiness,
  fetchVoiceCatalog,
  runJob,
} from "../lib/api";
import type { CreateJobInput, JobDetail, JobStatus, RecentJob, RuntimeReadiness, VoiceCatalog } from "../lib/types";

export default function HomePage() {
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [voiceCatalog, setVoiceCatalog] = useState<VoiceCatalog | null>(null);
  const [runtimeReadiness, setRuntimeReadiness] = useState<RuntimeReadiness | null>(null);
  const [duration, setDuration] = useState<15 | 30 | 60>(30);
  const [shotCount, setShotCount] = useState<3 | 5 | 7>(5);
  const [subtitlesEnabled, setSubtitlesEnabled] = useState(true);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [currentJob, setCurrentJob] = useState<JobDetail | null>(null);
  const [recentJobs, setRecentJobs] = useState<RecentJob[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    if (!currentJobId) {
      return;
    }

    const jobId = currentJobId;
    let active = true;
    let timeoutId: ReturnType<typeof setTimeout> | null = null;
    const terminalStatuses = new Set(["completed", "failed", "degraded"]);

    async function pollJob() {
      try {
        const detail = await fetchJobDetail(jobId);
        if (!active) {
          return;
        }
        setCurrentJob(detail);
        if (terminalStatuses.has(detail.status)) {
          setIsGenerating(false);
          return;
        }
        timeoutId = setTimeout(() => {
          void pollJob();
        }, 2000);
      } catch (error) {
        if (!active) {
          return;
        }
        setSubmitError(error instanceof Error ? error.message : "获取任务状态失败");
        setIsGenerating(false);
      }
    }

    void pollJob();

    return () => {
      active = false;
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [currentJobId]);

  useEffect(() => {
    let active = true;

    async function loadVoiceCatalog() {
      try {
        const [catalog, readiness] = await Promise.all([
          fetchVoiceCatalog(),
          fetchRuntimeReadiness().catch(() => null),
        ]);
        const jobs = await fetchRecentJobs().catch(() => []);
        if (active) {
          setVoiceCatalog(catalog);
          setRuntimeReadiness(readiness);
          setRecentJobs(jobs);
        }
      } catch {
        if (active) {
          setVoiceCatalog(null);
          setRuntimeReadiness(null);
          setRecentJobs([]);
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
    setCurrentJob(null);
    setCurrentJobId(null);
    setIsGenerating(true);

    try {
      const job = await createJob({
        ...value,
        duration,
        shotCount,
        subtitlesEnabled,
      });
      const nextRecentJob: RecentJob = {
        jobId: job.job_id,
        topic: job.topic,
        style: job.style,
        status: "pending" as JobStatus,
        createdAt: new Date().toISOString(),
      };
      setRecentJobs((existing) => [
        nextRecentJob,
        ...existing.filter((item) => item.jobId !== job.job_id),
      ].slice(0, 10));
      setCurrentJobId(job.job_id);
      setCurrentJob(await fetchJobDetail(job.job_id));
      void runJob(job.job_id).catch((error) => {
        setSubmitError(error instanceof Error ? error.message : "提交任务失败");
        setIsGenerating(false);
      });
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "提交任务失败");
      setIsGenerating(false);
    }
  }

  return (
    <main className="workbench-shell">
      <section className="workbench-hero">
        <div className="hero-copy">
          <p className="hero-kicker">VideoMind</p>
          <h1>VideoMind</h1>
          <p className="hero-description">
            输入主题与风格，配置核心参数后，系统会以冷启动工作流生成更接近真实创作平台体验的中文短视频。
          </p>
        </div>
      </section>

      <section className="workbench-top-grid">
        <div className="workbench-top-primary">
          <JobForm
            disabled={isGenerating}
            duration={duration}
            onSubmit={handleSubmit}
            shotCount={shotCount}
            subtitlesEnabled={subtitlesEnabled}
            voiceOptions={voiceCatalog?.voices}
          />
          {submitError ? <p className="error-banner" role="alert">{submitError}</p> : null}
        </div>
        <GenerationControls
          disabled={isGenerating}
          duration={duration}
          onDurationChange={setDuration}
          onShotCountChange={setShotCount}
          onSubtitlesEnabledChange={setSubtitlesEnabled}
          shotCount={shotCount}
          subtitlesEnabled={subtitlesEnabled}
        />
      </section>

      <section className="workbench-bottom-grid">
        <RuntimePanel readiness={runtimeReadiness} voiceCatalog={voiceCatalog} />
        <RecentJobsPanel jobs={recentJobs} />
        <CurrentJobPanel isGenerating={isGenerating} job={currentJob} />
      </section>
    </main>
  );
}
