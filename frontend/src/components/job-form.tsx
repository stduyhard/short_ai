"use client";

import React, { useState } from "react";
import type { CreateJobInput, VoiceOption } from "../lib/types";

type JobFormProps = {
  onSubmit?: (value: CreateJobInput) => void | Promise<void>;
  voiceOptions?: VoiceOption[];
  duration?: 15 | 30 | 60;
  shotCount?: 3 | 5 | 7;
  subtitlesEnabled?: boolean;
};

const DEFAULT_VOICE_OPTIONS: VoiceOption[] = [
  { value: "auto", label: "自动匹配" },
  { value: "Chelsie", label: "Chelsie" },
  { value: "Serena", label: "Serena" },
  { value: "Ethan", label: "Ethan" },
  { value: "Dylan", label: "Dylan" },
];

export function JobForm({
  onSubmit,
  voiceOptions = DEFAULT_VOICE_OPTIONS,
  duration = 30,
  shotCount = 5,
  subtitlesEnabled = true,
}: JobFormProps) {
  const [topic, setTopic] = useState("");
  const [style, setStyle] = useState("");
  const [voice, setVoice] = useState("auto");

  return (
    <form
      className="workbench-card workbench-form"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit?.({ topic, style, voice, duration, shotCount, subtitlesEnabled });
      }}
    >
      <label className="field-label" htmlFor="topic">
        主题
      </label>
      <input
        className="field-input"
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
      <button className="primary-button" type="submit">
        开始生成
      </button>
    </form>
  );
}
