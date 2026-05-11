"use client";

import React from "react";

type GenerationControlsProps = {
  duration: 15 | 30 | 60;
  shotCount: 3 | 5 | 7;
  subtitlesEnabled: boolean;
  onDurationChange: (value: 15 | 30 | 60) => void;
  onShotCountChange: (value: 3 | 5 | 7) => void;
  onSubtitlesEnabledChange: (value: boolean) => void;
  disabled?: boolean;
};

const DURATIONS = [15, 30, 60] as const;
const SHOT_COUNTS = [3, 5, 7] as const;

export function GenerationControls({
  duration,
  shotCount,
  subtitlesEnabled,
  onDurationChange,
  onShotCountChange,
  onSubtitlesEnabledChange,
  disabled = false,
}: GenerationControlsProps) {
  return (
    <section className="workbench-card control-card" aria-label="视频基础参数">
      <p className="panel-kicker">Generation Controls</p>
      <h2>视频基础参数</h2>
      <p className="panel-copy">这组参数会真实进入任务请求与工作流，不是静态占位。</p>

      <div className="control-group">
        <span className="control-label">时长</span>
        <div className="pill-row">
          {DURATIONS.map((value) => (
            <button
              key={value}
              className="pill-button"
              disabled={disabled}
              type="button"
              aria-pressed={duration === value}
              onClick={() => onDurationChange(value)}
            >
              {value}s
            </button>
          ))}
        </div>
      </div>

      <div className="control-group">
        <span className="control-label">画幅</span>
        <div className="aspect-card">9:16 竖屏</div>
      </div>

      <div className="control-group">
        <span className="control-label">分镜数量</span>
        <div className="pill-row">
          {SHOT_COUNTS.map((value) => (
            <button
              key={value}
              className="pill-button"
              disabled={disabled}
              type="button"
              aria-pressed={shotCount === value}
              onClick={() => onShotCountChange(value)}
            >
              {value} 镜头
            </button>
          ))}
        </div>
      </div>

      <div className="control-group">
        <span className="control-label">字幕</span>
        <label className="switch-row">
          <input
            aria-label="字幕"
            checked={subtitlesEnabled}
            disabled={disabled}
            onChange={(event) => onSubtitlesEnabledChange(event.target.checked)}
            role="switch"
            type="checkbox"
          />
          <span>{subtitlesEnabled ? "开启" : "关闭"}</span>
        </label>
      </div>
    </section>
  );
}
