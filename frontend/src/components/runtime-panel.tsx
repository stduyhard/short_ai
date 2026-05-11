import React from "react";
import type { RuntimeReadiness, VoiceCatalog } from "../lib/types";

type RuntimePanelProps = {
  voiceCatalog: VoiceCatalog | null;
  readiness: RuntimeReadiness | null;
};

export function RuntimePanel({ voiceCatalog, readiness }: RuntimePanelProps) {
  const ffmpegReady = readiness?.ffmpegAvailable ?? false;
  const providersReady = readiness?.providersConfigured ?? false;

  return (
    <aside className="workbench-card runtime-card" aria-label="运行状态">
      <p className="panel-kicker">Runtime</p>
      <h2>运行状态</h2>
      <p className="runtime-primary">
        当前音色目录：
        {voiceCatalog ? `${voiceCatalog.provider} / ${voiceCatalog.model}` : "加载中"}
      </p>
      <div className="readiness-strip">
        <span className={`readiness-badge${providersReady ? " is-ready" : " is-blocked"}`}>
          {providersReady ? "Provider 已就绪" : "Provider 未就绪"}
        </span>
        <span className={`readiness-badge${ffmpegReady ? " is-ready" : " is-blocked"}`}>
          {ffmpegReady ? "ffmpeg 已就绪" : "ffmpeg 未就绪"}
        </span>
      </div>

      <div className="status-stack">
        <div className="status-item">
          <span className="status-dot" />
          <div>
            <strong>创建任务</strong>
            <p>点击开始生成后，系统会先创建任务，并立刻触发工作流运行。</p>
          </div>
        </div>
        <div className="status-item">
          <span className="status-dot" />
          <div>
            <strong>真实出片前提</strong>
            <p>需要 provider 配置完成，并且 `ffmpeg` 已经就绪，才能输出真实成片。</p>
          </div>
        </div>
        <div className="status-item">
          <span className="status-dot" />
          <div>
            <strong>结果预览入口</strong>
            <p>任务创建成功后，首页会直接显示进度、素材、配音和最终成片。</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
