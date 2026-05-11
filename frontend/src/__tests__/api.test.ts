import { describe, expect, test } from "vitest";

import { resolveApiBaseUrl, toPublicArtifactUrl } from "../lib/api";

describe("api url helpers", () => {
  test("falls back to the default local backend port", () => {
    expect(resolveApiBaseUrl()).toBe("http://127.0.0.1:8001");
  });

  test("trims whitespace around configured api base url", () => {
    expect(resolveApiBaseUrl(" http://127.0.0.1:8001 \n")).toBe("http://127.0.0.1:8001");
  });

  test("removes trailing slash from configured api base url", () => {
    expect(resolveApiBaseUrl("http://127.0.0.1:8001/")).toBe("http://127.0.0.1:8001");
  });

  test("builds public artifact url from windows path using normalized base url", () => {
    expect(
      toPublicArtifactUrl(
        "D:\\short_video\\artifacts\\renders\\job-1\\final.mp4",
        " http://127.0.0.1:8001/ "
      )
    ).toBe("http://127.0.0.1:8001/artifacts/renders/job-1/final.mp4");
  });
});
