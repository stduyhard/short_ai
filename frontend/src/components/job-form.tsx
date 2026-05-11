"use client";

import React, { useState } from "react";
import type { CreateJobInput, VoiceOption } from "../lib/types";

type JobFormProps = {
  onSubmit?: (value: CreateJobInput) => void | Promise<void>;
  voiceOptions?: VoiceOption[];
  duration?: 15 | 30 | 60;
  shotCount?: 3 | 5 | 7;
  subtitlesEnabled?: boolean;
  disabled?: boolean;
};

const DEFAULT_VOICE_OPTIONS: VoiceOption[] = [
  { value: "auto", label: "自动匹配" },
  { value: "Chelsie", label: "Chelsie" },
  { value: "Seren", label: "Seren" },
  { value: "Ethan", label: "Ethan" },
  { value: "Dylan", label: "Dylan" },
];

export function JobForm({
  onSubmit,
  voiceOptions = DEFAULT_VOICE_OPTIONS,
  duration = 30,
  shotCount = 5,
  subtitlesEnabled = true,
  disabled = false,
}: JobFormProps) {
  const [topic, setTopic] = useState("");
  const [style, setStyle] = useState("");
  const [voice, setVoice] = useState("auto");
  const [formError, setFormError] = useState<string | null>(null);

  return (
    <form
      className="workbench-card workbench-form"
      onSubmit={(event) => {
        event.preventDefault();
        const normalizedTopic = topic.trim();
        const normalizedStyle = style.trim();

        if (!normalizedTopic || !normalizedStyle) {
          setFormError("请先填写主题和风格");
          return;
        }

        setFormError(null);
        onSubmit?.({
          topic: normalizedTopic,
          style: normalizedStyle,
          voice,
          duration,
          shotCount,
          subtitlesEnabled,
        });
      }}
    >
      <label className="field-label" htmlFor="topic">
        主题
      </label>
      <input
        className="field-input"
        disabled={disabled}
        id="topic"
        name="topic"
        value={topic}
        onChange={(event) => setTopic(event.target.value)}
        placeholder="比如：职场新人如何快速成长"
      />
      <label className="field-label" htmlFor="style">
        风格
      </label>
      <input
        className="field-input"
        disabled={disabled}
        id="style"
        name="style"
        value={style}
        onChange={(event) => setStyle(event.target.value)}
        placeholder="比如：治愈干货 / 口播感"
      />
      <label className="field-label" htmlFor="voice">
        音色
      </label>
      <select
        className="field-input"
        disabled={disabled}
        id="voice"
        name="voice"
        value={voice}
        onChange={(event) => setVoice(event.target.value)}
      >
        {voiceOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {formError ? <p className="form-error" role="alert">{formError}</p> : null}
      <button className="primary-button" disabled={disabled} type="submit">
        {disabled ? "生成中..." : "开始生成"}
      </button>
    </form>
  );
}
