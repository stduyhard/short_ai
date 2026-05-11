import "@testing-library/jest-dom/vitest";
import React from "react";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import HomePage from "../app/page";
import { JobForm } from "../components/job-form";
import { createJob, fetchJobDetail, fetchRecentJobs, fetchRuntimeReadiness, fetchVoiceCatalog, runJob } from "../lib/api";

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: pushMock,
  }),
}));

vi.mock("../lib/api", () => ({
  createJob: vi.fn(),
  fetchJobDetail: vi.fn(),
  fetchRecentJobs: vi.fn(),
  runJob: vi.fn(),
  fetchVoiceCatalog: vi.fn(),
  fetchRuntimeReadiness: vi.fn(),
}));

afterEach(() => {
  cleanup();
});

beforeEach(() => {
  pushMock.mockReset();
  vi.mocked(createJob).mockReset();
  vi.mocked(fetchJobDetail).mockReset();
  vi.mocked(fetchRecentJobs).mockReset();
  vi.mocked(runJob).mockReset();
  vi.mocked(fetchVoiceCatalog).mockReset();
  vi.mocked(fetchRuntimeReadiness).mockReset();
  vi.mocked(fetchVoiceCatalog).mockResolvedValue({
    provider: "qwen",
    model: "qwen3-tts-flash",
    voices: [
      { value: "auto", label: "自动匹配" },
      { value: "Chelsie", label: "Chelsie" },
    ],
  });
  vi.mocked(fetchRuntimeReadiness).mockResolvedValue({
    providersConfigured: true,
    ffmpegAvailable: false,
    readyForRealGeneration: false,
  });
  vi.mocked(fetchRecentJobs).mockResolvedValue([
    {
      jobId: "recent-1",
      topic: "最近任务一",
      style: "轻松口播",
      status: "completed",
      createdAt: "2026-05-10T20:40:00Z",
    },
  ]);
  vi.mocked(fetchJobDetail).mockResolvedValue({
    jobId: "job-123",
    topic: "春节旅行攻略",
    style: "轻松口播",
    voiceSelection: "auto",
    duration: 60,
    shotCount: 7,
    subtitlesEnabled: false,
    aspectRatio: "9:16",
    status: "running",
    stages: [
      { key: "director", label: "创意策划", status: "running" },
      { key: "script", label: "文案生成", status: "pending" },
    ],
    visualAssets: null,
    voiceAsset: null,
    finalVideo: null,
  });
});

describe("JobForm", () => {
  it("renders topic and style inputs", () => {
    render(<JobForm />);

    expect(screen.getByLabelText("主题")).toBeInTheDocument();
    expect(screen.getByLabelText("风格")).toBeInTheDocument();
    expect(screen.getByLabelText("音色")).toBeInTheDocument();
    expect(screen.getByDisplayValue("自动匹配")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "开始生成" })).toBeInTheDocument();
  });

  it("submits topic and style values with auto voice by default", () => {
    const handleSubmit = vi.fn();

    render(<JobForm onSubmit={handleSubmit} />);

    fireEvent.change(screen.getByLabelText("主题"), {
      target: { value: "春节旅行攻略" },
    });
    fireEvent.change(screen.getByLabelText("风格"), {
      target: { value: "轻松口播" },
    });
    fireEvent.click(screen.getByRole("button", { name: "开始生成" }));

    expect(handleSubmit).toHaveBeenCalledWith({
      topic: "春节旅行攻略",
      style: "轻松口播",
      voice: "auto",
      duration: 30,
      shotCount: 5,
      subtitlesEnabled: true,
    });
  });

  it("blocks submission when topic or style is empty", () => {
    const handleSubmit = vi.fn();

    render(<JobForm onSubmit={handleSubmit} />);

    fireEvent.click(screen.getByRole("button", { name: "开始生成" }));

    expect(handleSubmit).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent("请先填写主题和风格");
  });

  it("submits a manually selected voice", () => {
    const handleSubmit = vi.fn();

    render(<JobForm onSubmit={handleSubmit} />);

    fireEvent.change(screen.getByLabelText("主题"), {
      target: { value: "春节旅行攻略" },
    });
    fireEvent.change(screen.getByLabelText("风格"), {
      target: { value: "轻松口播" },
    });
    fireEvent.change(screen.getByLabelText("音色"), {
      target: { value: "Chelsie" },
    });
    fireEvent.click(screen.getByRole("button", { name: "开始生成" }));

    expect(handleSubmit).toHaveBeenCalledWith({
      topic: "春节旅行攻略",
      style: "轻松口播",
      voice: "Chelsie",
      duration: 30,
      shotCount: 5,
      subtitlesEnabled: true,
    });
  });

  it("submits on the home page and keeps generation on the current page", async () => {
    vi.mocked(createJob).mockResolvedValue({
      job_id: "job-123",
      topic: "春节旅行攻略",
      style: "轻松口播",
      status: "pending",
    });
    vi.mocked(runJob).mockResolvedValue({
      jobId: "job-123",
      status: "running",
    });

    render(<HomePage />);

    fireEvent.change(screen.getByLabelText("主题"), {
      target: { value: "春节旅行攻略" },
    });
    fireEvent.change(screen.getByLabelText("风格"), {
      target: { value: "轻松口播" },
    });
    fireEvent.click(screen.getByRole("button", { name: "60s" }));
    fireEvent.click(screen.getByRole("button", { name: "7 镜头" }));
    fireEvent.click(screen.getByRole("switch", { name: "字幕" }));
    fireEvent.click(screen.getByRole("button", { name: "开始生成" }));

    await waitFor(() => {
      expect(createJob).toHaveBeenCalledWith({
        topic: "春节旅行攻略",
        style: "轻松口播",
        voice: "auto",
        duration: 60,
        shotCount: 7,
        subtitlesEnabled: false,
      });
    });

    await waitFor(() => {
      expect(runJob).toHaveBeenCalledWith("job-123");
    });

    await waitFor(() => {
      expect(fetchJobDetail).toHaveBeenCalledWith("job-123");
    });

    expect(pushMock).not.toHaveBeenCalled();
    expect(screen.getByText("当前生成结果")).toBeInTheDocument();
    expect(screen.getByText("状态：running")).toBeInTheDocument();
  });

  it("shows the current voice catalog source on the home page", async () => {
    render(<HomePage />);

    await waitFor(() => {
      expect(screen.getByText("当前音色目录：qwen / qwen3-tts-flash")).toBeInTheDocument();
    });
  });

  it("shows an error on the home page when createJob fails", async () => {
    vi.mocked(createJob).mockRejectedValue(new Error("Failed to create job"));

    render(<HomePage />);

    fireEvent.change(screen.getByLabelText("主题"), {
      target: { value: "春节旅行攻略" },
    });
    fireEvent.change(screen.getByLabelText("风格"), {
      target: { value: "轻松口播" },
    });
    fireEvent.click(screen.getByRole("button", { name: "开始生成" }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Failed to create job");
    });

    expect(pushMock).not.toHaveBeenCalled();
  });

  it("renders the homepage workbench layout", async () => {
    render(<HomePage />);

    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1, name: "VideoMind" })).toBeInTheDocument();
    });

    expect(screen.getByText("视频基础参数")).toBeInTheDocument();
    expect(screen.getByText("运行状态")).toBeInTheDocument();
    expect(screen.getByText("当前音色目录：qwen / qwen3-tts-flash")).toBeInTheDocument();
    expect(screen.getByText("ffmpeg 未就绪")).toBeInTheDocument();
    expect(screen.getByText("最近任务")).toBeInTheDocument();
    expect(screen.getByText("最近任务一")).toBeInTheDocument();
  });
});
