"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { runJob } from "../lib/api";

type RunJobButtonProps = {
  jobId: string;
};

export function RunJobButton({ jobId }: RunJobButtonProps) {
  const router = useRouter();
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRun() {
    setIsRunning(true);
    setError(null);

    try {
      await runJob(jobId);
      router.refresh();
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "任务运行失败");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <div style={{ margin: "12px 0 20px" }}>
      <button className="primary-button" disabled={isRunning} onClick={handleRun} type="button">
        {isRunning ? "运行中..." : "立即运行任务"}
      </button>
      {error ? <p role="alert">{error}</p> : null}
    </div>
  );
}
