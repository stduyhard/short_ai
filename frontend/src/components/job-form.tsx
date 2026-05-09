"use client";

import React, { useState } from "react";
import type { CreateJobInput } from "../lib/types";

type JobFormProps = {
  onSubmit?: (value: CreateJobInput) => void | Promise<void>;
};

export function JobForm({ onSubmit }: JobFormProps) {
  const [topic, setTopic] = useState("");
  const [style, setStyle] = useState("");

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit?.({ topic, style });
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
      <button type="submit">开始生成</button>
    </form>
  );
}
