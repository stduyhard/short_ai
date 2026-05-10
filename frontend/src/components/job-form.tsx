"use client";

import React, { useState } from "react";
import type { CreateJobInput } from "../lib/types";

type JobFormProps = {
  onSubmit?: (value: CreateJobInput) => void | Promise<void>;
};

export function JobForm({ onSubmit }: JobFormProps) {
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
        <option value="auto">自动匹配</option>
        <option value="Chelsie">Chelsie</option>
        <option value="Serena">Serena</option>
        <option value="Ethan">Ethan</option>
        <option value="Dylan">Dylan</option>
      </select>
      <button type="submit">开始生成</button>
    </form>
  );
}
