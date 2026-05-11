import React from "react";
import { AudioPreview } from "../../../components/audio-preview";
import { JobStageList } from "../../../components/job-stage-list";
import { RunJobButton } from "../../../components/run-job-button";
import { VideoPreview } from "../../../components/video-preview";
import { fetchJobDetail, toPublicArtifactUrl } from "../../../lib/api";

type JobDetailPageProps = {
  params: Promise<{
    jobId: string;
  }>;
};

function formatStatus(status: string) {
  switch (status) {
    case "completed":
      return "已完成";
    case "running":
      return "生成中";
    case "failed":
      return "失败";
    case "degraded":
      return "降级完成";
    default:
      return "待处理";
  }
}

export default async function JobDetailPage({ params }: JobDetailPageProps) {
  const { jobId } = await params;
  let job;

  try {
    job = await fetchJobDetail(jobId);
  } catch {
    return (
      <main className="job-detail-shell">
        <section className="job-detail-hero workbench-card">
          <p className="panel-kicker">Job Detail</p>
          <h1>任务不存在</h1>
          <p className="panel-copy">
            当前任务 ID 在正在运行的后端实例中找不到，通常是因为本地服务重启后内存任务已失效。
          </p>
          <p className="job-detail-backlink">
            请返回首页重新创建任务：
            <a href="/"> http://127.0.0.1:3000/</a>
          </p>
        </section>
      </main>
    );
  }

  return (
    <main className="job-detail-shell">
      <section className="job-detail-hero workbench-card">
        <div className="job-detail-heading">
          <div>
            <p className="panel-kicker">Job Detail</p>
            <h1>任务详情</h1>
            <p className="panel-copy">
              查看当前任务的生成进度、参数、文案素材与最终成片。
            </p>
          </div>
          <span className={`result-status is-${job.status}`}>状态：{formatStatus(job.status)}</span>
        </div>
        <div className="job-summary-grid">
          <div className="job-summary-card">
            <span>主题</span>
            <strong>{job.topic}</strong>
          </div>
          <div className="job-summary-card">
            <span>风格</span>
            <strong>{job.style}</strong>
          </div>
          <div className="job-summary-card">
            <span>任务 ID</span>
            <strong>{job.jobId}</strong>
          </div>
          <div className="job-summary-card">
            <span>音色</span>
            <strong>{job.voiceSelection}</strong>
          </div>
        </div>
        {job.errorMessage ? <p className="inline-error">错误信息：{job.errorMessage}</p> : null}
        {job.status === "pending" ? <RunJobButton jobId={job.jobId} /> : null}
      </section>

      <section className="job-detail-grid">
        <div className="job-detail-main">
          <section className="workbench-card detail-card">
            <JobStageList stages={job.stages} />
          </section>

          <section className="workbench-card detail-card">
            <p className="panel-kicker">Parameters</p>
            <h2>生成参数</h2>
            <div className="detail-parameter-grid">
              <div className="detail-parameter-item">
                <span>时长</span>
                <strong>{job.duration}s</strong>
              </div>
              <div className="detail-parameter-item">
                <span>分镜数量</span>
                <strong>{job.shotCount}</strong>
              </div>
              <div className="detail-parameter-item">
                <span>字幕</span>
                <strong>{job.subtitlesEnabled ? "开启" : "关闭"}</strong>
              </div>
              <div className="detail-parameter-item">
                <span>画幅</span>
                <strong>{job.aspectRatio}</strong>
              </div>
            </div>
          </section>

          <section className="workbench-card detail-card">
            <p className="panel-kicker">Creative Brief</p>
            <h2>创意 Brief</h2>
            <p className="detail-rich-copy">{job.brief ?? "暂未生成"}</p>
          </section>

          <section className="workbench-card detail-card">
            <p className="panel-kicker">Script</p>
            <h2>文案</h2>
            {job.script ? (
              <div className="script-preview detail-script-preview">
                {job.script.split("\n").map((line, index) => (
                  <p key={`${job.jobId}-script-${index}`}>{line}</p>
                ))}
              </div>
            ) : (
              <p className="panel-copy">暂未生成</p>
            )}
          </section>

          <section className="workbench-card detail-card">
            <p className="panel-kicker">Storyboard</p>
            <h2>分镜</h2>
            {job.storyboard?.length ? (
              <ul className="storyboard-list">
                {job.storyboard.map((shot, index) => (
                  <li key={`${shot.shot}-${index}`} className="storyboard-item">
                    <strong>镜头 {shot.shot}</strong>
                    <p>{shot.caption}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="panel-copy">暂未生成</p>
            )}
          </section>
        </div>

        <aside className="job-detail-side">
          <section className="workbench-card detail-card">
            <p className="panel-kicker">Visual Assets</p>
            <h2>视觉素材</h2>
            {job.visualAssets?.length ? (
              <div className="asset-grid asset-grid--detail">
                {job.visualAssets.map((asset) => {
                  const src = toPublicArtifactUrl(asset);
                  return src ? (
                    <figure key={asset} className="detail-asset-card">
                      <img className="asset-image" src={src} alt="生成视觉素材" />
                    </figure>
                  ) : (
                    <p key={asset}>{asset}</p>
                  );
                })}
              </div>
            ) : (
              <p className="panel-copy">暂未生成</p>
            )}
          </section>

          <section className="workbench-card detail-card">
            <p className="panel-kicker">Voice Over</p>
            <h2>配音音频</h2>
            <AudioPreview
              className="detail-audio-player"
              src={job.voiceAsset ? (toPublicArtifactUrl(job.voiceAsset) ?? job.voiceAsset) : undefined}
            />
            {job.voiceAsset ? <p className="detail-path-copy">原始路径：{job.voiceAsset}</p> : null}
          </section>

          <section className="workbench-card detail-card detail-card--video">
            <p className="panel-kicker">Final Video</p>
            <h2>成片预览</h2>
            <div className="detail-video-wrap">
              <VideoPreview
                className="media-frame--detail"
                src={job.finalVideo ? (toPublicArtifactUrl(job.finalVideo) ?? job.finalVideo) : undefined}
              />
            </div>
            {job.finalVideo ? <p className="detail-path-copy">成片路径：{job.finalVideo}</p> : null}
          </section>
        </aside>
      </section>
    </main>
  );
}
