import React from "react";
import { AudioPreview } from "./audio-preview";
import { JobStageList } from "./job-stage-list";
import { VideoPreview } from "./video-preview";
import { toPublicArtifactUrl } from "../lib/api";
import type { JobDetail } from "../lib/types";

type CurrentJobPanelProps = {
  job: JobDetail | null;
  isGenerating: boolean;
};

export function CurrentJobPanel({ job, isGenerating }: CurrentJobPanelProps) {
  return (
    <section className="workbench-card current-job-card" aria-label="当前生成结果">
      <p className="panel-kicker">Current Job</p>
      <h2>当前生成结果</h2>
      <p className="panel-copy">
        {isGenerating
          ? "任务正在当前页运行，图片、音频和最终视频会在这里刷新。"
          : "生成完成后，图片、音频和成片会在这里预览。"}
      </p>

      {!job ? (
        <div className="empty-state">
          <strong>还没有开始生成</strong>
          <p>填写主题和风格后点击“开始生成”，当前页会显示进度和结果。</p>
        </div>
      ) : (
        <div className="result-stack">
          <div className="result-meta">
            <strong>{job.topic}</strong>
            <span className={`result-status is-${job.status}`}>状态：{job.status}</span>
          </div>
          {job.errorMessage ? <p className="inline-error">失败原因：{job.errorMessage}</p> : null}
          <JobStageList stages={job.stages} />

          <section className="asset-section">
            <h3>视觉素材</h3>
            {job.visualAssets?.length ? (
              <div className="asset-grid">
                {job.visualAssets.map((asset) => {
                  const src = toPublicArtifactUrl(asset);
                  return src ? (
                    <img key={asset} className="asset-image" src={src} alt="生成视觉素材" />
                  ) : (
                    <p key={asset}>{asset}</p>
                  );
                })}
              </div>
            ) : (
              <p>图片生成后会在这里显示。</p>
            )}
          </section>

          <section className="asset-section">
            <h3>配音文案</h3>
            {job.script ? (
              <div className="script-preview">
                {job.script.split("\n").map((line, index) => (
                  <p key={`${job.jobId}-script-${index}`}>{line}</p>
                ))}
              </div>
            ) : (
              <p>配音文案生成后会在这里显示。</p>
            )}
          </section>

          <section className="asset-section">
            <h3>配音音频</h3>
            <AudioPreview
              className="detail-audio-player"
              src={job.voiceAsset ? (toPublicArtifactUrl(job.voiceAsset) ?? job.voiceAsset) : undefined}
            />
          </section>

          <section className="asset-section">
            <h3>最终视频</h3>
            <VideoPreview
              className="media-frame--compact"
              src={job.finalVideo ? (toPublicArtifactUrl(job.finalVideo) ?? job.finalVideo) : undefined}
            />
          </section>
        </div>
      )}
    </section>
  );
}
