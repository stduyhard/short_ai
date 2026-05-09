import React from "react";

export function AudioPreview({ src }: { src?: string }) {
  if (!src) {
    return <p>音频生成后将在这里预览。</p>;
  }

  if (/^https?:\/\//.test(src) || /^[A-Za-z]:\\/.test(src) || src.startsWith("/")) {
    return <audio src={src} controls aria-label="配音预览" />;
  }

  return <p>配音路径：{src}</p>;
}
