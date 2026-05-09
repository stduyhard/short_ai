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
      {job.errorMessage ? <p>错误信息：{job.errorMessage}</p> : null}
      <JobStageList stages={job.stages} />

      <section>
        <h2>创意 Brief</h2>
        <p>{job.brief ?? "暂未生成"}</p>
      </section>

      <section>
        <h2>文案</h2>
        <p>{job.script ?? "暂未生成"}</p>
      </section>

      <section>
        <h2>分镜</h2>
        {job.storyboard?.length ? (
          <ul>
            {job.storyboard.map((shot, index) => (
              <li key={`${shot.shot}-${index}`}>
                镜头 {shot.shot}：{shot.caption}
              </li>
            ))}
          </ul>
        ) : (
          <p>暂未生成</p>
        )}
      </section>

      <section>
        <h2>视觉素材</h2>
        {job.visualAssets?.length ? (
          <ul>
            {job.visualAssets.map((asset) => (
              <li key={asset}>{asset}</li>
            ))}
          </ul>
        ) : (
          <p>暂未生成</p>
        )}
      </section>

      <section>
        <h2>配音音频</h2>
        <p>{job.voiceAsset ?? "暂未生成"}</p>
      </section>

      <section>
        <h2>成片预览</h2>
        <VideoPreview src={job.finalVideo ?? undefined} />
      </section>
    </main>
  );
}
