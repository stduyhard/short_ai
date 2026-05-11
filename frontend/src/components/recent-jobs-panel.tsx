import React from "react";
import type { RecentJob } from "../lib/types";

type RecentJobsPanelProps = {
  jobs: RecentJob[];
};

export function RecentJobsPanel({ jobs }: RecentJobsPanelProps) {
  return (
    <aside className="workbench-card runtime-card" aria-label="最近任务">
      <p className="panel-kicker">Recent Jobs</p>
      <h2>最近任务</h2>
      {jobs.length === 0 ? (
        <p className="panel-copy">还没有历史任务，开始生成后会在这里保留最近记录。</p>
      ) : (
        <div className="recent-job-list">
          {jobs.map((job) => (
            <a key={job.jobId} className="recent-job-item" href={`/jobs/${job.jobId}`}>
              <div className="recent-job-topline">
                <strong>{job.topic}</strong>
                <span className={`result-status is-${job.status}`}>{job.status}</span>
              </div>
              <p>{job.style}</p>
              <span className="recent-job-time">{formatRecentTime(job.createdAt)}</span>
            </a>
          ))}
        </div>
      )}
    </aside>
  );
}

function formatRecentTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}
