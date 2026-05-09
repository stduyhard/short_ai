import React from "react";
import { JobStageList } from "../../../components/job-stage-list";
import { VideoPreview } from "../../../components/video-preview";
import type { JobDetail } from "../../../lib/types";

const defaultStages: JobDetail["stages"] = [
  { key: "director", label: "创意策划", status: "pending" },
  { key: "script", label: "文案生成", status: "pending" },
  { key: "storyboard", label: "分镜生成", status: "pending" },
  { key: "visual", label: "视觉素材生成", status: "pending" },
  { key: "voice", label: "配音与字幕生成", status: "pending" },
  { key: "editor", label: "视频渲染", status: "pending" },
];

type JobDetailPageProps = {
  params: Promise<{
    jobId: string;
  }>;
};

export default async function JobDetailPage({ params }: JobDetailPageProps) {
  const { jobId } = await params;

  return (
    <main>
      <h1>任务详情</h1>
      <p>任务 ID：{jobId}</p>
      <JobStageList stages={defaultStages} />
      <VideoPreview />
    </main>
  );
}
