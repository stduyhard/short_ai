import "@testing-library/jest-dom/vitest";
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AudioPreview } from "../components/audio-preview";

describe("AudioPreview", () => {
  it("renders an audio player for public sources", () => {
    render(<AudioPreview src="http://127.0.0.1:8000/artifacts/jobs/job-1/voice.mp3" />);

    expect(screen.getByLabelText("配音预览")).toBeInTheDocument();
  });

  it("renders placeholder copy when no source is available", () => {
    render(<AudioPreview />);

    expect(screen.getByText("音频生成后将在这里预览。")).toBeInTheDocument();
  });

  it("renders the raw path when the source is not publicly accessible", () => {
    render(<AudioPreview src="voice-output.mp3" />);

    expect(screen.getByText("配音路径：voice-output.mp3")).toBeInTheDocument();
  });
});
