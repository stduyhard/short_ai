import "@testing-library/jest-dom/vitest";
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { JobForm } from "../components/job-form";

describe("JobForm", () => {
  it("renders topic and style inputs", () => {
    render(<JobForm />);

    expect(screen.getByLabelText("主题")).toBeInTheDocument();
    expect(screen.getByLabelText("风格")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "开始生成" })).toBeInTheDocument();
  });
});
