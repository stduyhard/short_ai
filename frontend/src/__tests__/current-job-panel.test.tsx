import "@testing-library/jest-dom/vitest";
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CurrentJobPanel } from "../components/current-job-panel";

describe("CurrentJobPanel", () => {
  it("renders the normalized voiceover script alongside the audio section", () => {
    render(
      <CurrentJobPanel
        isGenerating={false}
        job={{
          jobId: "job-voice",
          topic: "晨光短片",
          style: "治愈",
          voiceSelection: "auto",
          duration: 15,
          shotCount: 3,
          subtitlesEnabled: true,
          aspectRatio: "9:16",
          status: "completed",
          stages: [],
          script: "它轻轻醒来，像一束还没说话的光。\n你看，世界正在慢慢发亮。",
          visualAssets: null,
          voiceAsset: "artifacts/audio/job-voice/voice.mp3",
          finalVideo: null,
        }}
      />
    );

    expect(screen.getByText("配音文案")).toBeInTheDocument();
    expect(screen.getByText("它轻轻醒来，像一束还没说话的光。")).toBeInTheDocument();
    expect(screen.getByText("你看，世界正在慢慢发亮。")).toBeInTheDocument();
  });
});
