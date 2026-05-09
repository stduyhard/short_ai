import "@testing-library/jest-dom/vitest";
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { JobStageList } from "../components/job-stage-list";

describe("JobStageList", () => {
  it("renders all pipeline stages", () => {
    render(
      <JobStageList
        stages={[
          { key: "director", label: "创意策划", status: "completed" },
          { key: "script", label: "文案生成", status: "running" },
          { key: "storyboard", label: "分镜生成", status: "pending" },
        ]}
      />,
    );

    expect(screen.getByText("创意策划")).toBeInTheDocument();
    expect(screen.getByText("文案生成")).toBeInTheDocument();
    expect(screen.getByText("分镜生成")).toBeInTheDocument();
  });
});
