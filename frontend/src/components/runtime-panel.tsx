import React from "react";
import type { VoiceCatalog } from "../lib/types";

type RuntimePanelProps = {
  voiceCatalog: VoiceCatalog | null;
};

export function RuntimePanel({ voiceCatalog }: RuntimePanelProps) {
  return (
    <aside className="workbench-card runtime-card" aria-label="运行状态">
      <p className="panel-kicker">Runtime</p>
      <h2>运行状态</h2>
      <p className="runtime-primary">
        当前音色目录：
        {voiceCatalog ? `${voiceCatalog.provider} / ${voiceCatalog.model}` : "加载中"}
      </p>

      <div className="status-stack">
        <div className="status-item">
          <span className="status-dot" />
          <div>
            <strong>创建任务</strong>
            <p>点击开始生成后，系统会先创建任务，再进入详情页执行后续工作流。</p>
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
            <p>任务创建成功后，会自动跳转详情页查看文案、素材、配音和成片状态。</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
