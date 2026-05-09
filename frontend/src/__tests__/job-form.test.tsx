import "@testing-library/jest-dom/vitest";
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HomePage from "../app/page";

describe("HomePage", () => {
  it("renders topic and style inputs", () => {
    render(<HomePage />);

    expect(screen.getByLabelText("主题")).toBeInTheDocument();
    expect(screen.getByLabelText("风格")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "开始生成" })).toBeInTheDocument();
  });
});
