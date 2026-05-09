import "@testing-library/jest-dom/vitest";
import React from "react";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import HomePage from "../app/page";
import { JobForm } from "../components/job-form";
import { createJob } from "../lib/api";

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: pushMock,
  }),
}));

vi.mock("../lib/api", () => ({
  createJob: vi.fn(),
}));

afterEach(() => {
  cleanup();
});

beforeEach(() => {
  pushMock.mockReset();
  vi.mocked(createJob).mockReset();
});

describe("JobForm", () => {
  it("renders topic and style inputs", () => {
    render(<JobForm />);

    expect(screen.getByLabelText("主题")).toBeInTheDocument();
    expect(screen.getByLabelText("风格")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "开始生成" })).toBeInTheDocument();
  });

  it("submits topic and style values", () => {
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
    });
  });

  it("submits on the home page and navigates with returned job_id", async () => {
    vi.mocked(createJob).mockResolvedValue({
      job_id: "job-123",
      topic: "春节旅行攻略",
      style: "轻松口播",
      status: "pending",
    });

    render(<HomePage />);

    fireEvent.change(screen.getByLabelText("主题"), {
      target: { value: "春节旅行攻略" },
    });
    fireEvent.change(screen.getByLabelText("风格"), {
      target: { value: "轻松口播" },
    });
    fireEvent.click(screen.getByRole("button", { name: "开始生成" }));

    await waitFor(() => {
      expect(createJob).toHaveBeenCalledWith({
        topic: "春节旅行攻略",
        style: "轻松口播",
      });
    });

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/jobs/job-123");
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
});
