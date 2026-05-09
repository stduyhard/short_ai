import React from "react";

export function VideoPreview({ src }: { src?: string }) {
  if (!src) {
    return <p>视频生成后将在这里预览。</p>;
  }

  if (/^https?:\/\//.test(src) || /^[A-Za-z]:\\/.test(src) || src.startsWith("/")) {
    return <video src={src} controls playsInline />;
  }

  return <p>成片路径：{src}</p>;
}
