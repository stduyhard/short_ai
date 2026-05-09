import React from "react";
import { JobStageList } from "../../../components/job-stage-list";
import { VideoPreview } from "../../../components/video-preview";
import { fetchJobDetail } from "../../../lib/api";

type JobDetailPageProps = {
  params: Promise<{
    jobId: string;
  }>;
};

export default async function JobDetailPage({ params }: JobDetailPageProps) {
  const { jobId } = await params;
  const job = await fetchJobDetail(jobId);

  return (
    <main>
      <h1>任务详情</h1>
      <p>任务 ID：{job.jobId}</p>
      <p>主题：{job.topic}</p>
      <p>风格：{job.style}</p>
      <p>状态：{job.status}</p>
      <JobStageList stages={job.stages} />
      <VideoPreview />
    </main>
  );
}
