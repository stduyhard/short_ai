import "@testing-library/jest-dom/vitest";
import React from "react";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { JobForm } from "../components/job-form";

afterEach(() => {
  cleanup();
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
});
