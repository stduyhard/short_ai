"use client";

import React, { useState } from "react";
import type { CreateJobInput, VoiceOption } from "../lib/types";

type JobFormProps = {
  onSubmit?: (value: CreateJobInput) => void | Promise<void>;
  voiceOptions?: VoiceOption[];
};

const DEFAULT_VOICE_OPTIONS: VoiceOption[] = [
  { value: "auto", label: "自动匹配" },
  { value: "Chelsie", label: "Chelsie" },
  { value: "Serena", label: "Serena" },
  { value: "Ethan", label: "Ethan" },
  { value: "Dylan", label: "Dylan" },
];

export function JobForm({ onSubmit, voiceOptions = DEFAULT_VOICE_OPTIONS }: JobFormProps) {
  const [topic, setTopic] = useState("");
  const [style, setStyle] = useState("");
  const [voice, setVoice] = useState("auto");

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit?.({ topic, style, voice });
      }}
    >
      <label htmlFor="topic">主题</label>
      <input
        id="topic"
        name="topic"
        value={topic}
        onChange={(event) => setTopic(event.target.value)}
      />
      <label htmlFor="style">风格</label>
      <input
        id="style"
        name="style"
        value={style}
        onChange={(event) => setStyle(event.target.value)}
      />
      <label htmlFor="voice">音色</label>
      <select
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
      <button type="submit">开始生成</button>
    </form>
  );
}
