import "@testing-library/jest-dom/vitest";
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { JobForm } from "../components/job-form";


describe("JobForm voice options", () => {
  it("renders voice options provided by the caller", () => {
    render(
      <JobForm
        voiceOptions={[
          { value: "auto", label: "自动匹配" },
          { value: "Chelsie", label: "Chelsie" },
          { value: "Serena", label: "Serena" },
        ]}
      />,
    );

    expect(screen.getByRole("option", { name: "自动匹配" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Chelsie" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Serena" })).toBeInTheDocument();
  });
});
