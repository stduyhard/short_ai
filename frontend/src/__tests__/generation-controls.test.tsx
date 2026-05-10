import "@testing-library/jest-dom/vitest";
import React from "react";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { GenerationControls } from "../components/generation-controls";


afterEach(() => {
  cleanup();
});


describe("GenerationControls", () => {
  it("renders duration, shot count, aspect ratio, and subtitles controls", () => {
    render(
      <GenerationControls
        duration={30}
        shotCount={5}
        subtitlesEnabled
        onDurationChange={vi.fn()}
        onShotCountChange={vi.fn()}
        onSubtitlesEnabledChange={vi.fn()}
      />
    );

    expect(screen.getByText("视频基础参数")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "15s" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "30s" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("9:16 竖屏")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "5 镜头" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("switch", { name: "字幕" })).toBeChecked();
  });

  it("calls change handlers when controls are updated", () => {
    const onDurationChange = vi.fn();
    const onShotCountChange = vi.fn();
    const onSubtitlesEnabledChange = vi.fn();

    render(
      <GenerationControls
        duration={15}
        shotCount={3}
        subtitlesEnabled
        onDurationChange={onDurationChange}
        onShotCountChange={onShotCountChange}
        onSubtitlesEnabledChange={onSubtitlesEnabledChange}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "60s" }));
    fireEvent.click(screen.getByRole("button", { name: "7 镜头" }));
    fireEvent.click(screen.getByRole("switch", { name: "字幕" }));

    expect(onDurationChange).toHaveBeenCalledWith(60);
    expect(onShotCountChange).toHaveBeenCalledWith(7);
    expect(onSubtitlesEnabledChange).toHaveBeenCalledWith(false);
  });
});
