import React from "react";
import type { JobStage, StageStatus } from "../lib/types";

const statusLabelMap: Record<StageStatus, string> = {
  pending: "待处理",
  running: "进行中",
  completed: "已完成",
  failed: "失败",
};

export function JobStageList({ stages }: { stages: JobStage[] }) {
  return (
    <section aria-labelledby="job-stage-list-title">
      <h2 id="job-stage-list-title">生成进度</h2>
      <ul>
        {stages.map((stage) => (
          <li key={stage.key}>
            <strong>{stage.label}</strong>
            <span>{statusLabelMap[stage.status]}</span>
            {stage.message ? <p>{stage.message}</p> : null}
          </li>
        ))}
      </ul>
    </section>
  );
}
