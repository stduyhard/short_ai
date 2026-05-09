import React from "react";

export function VideoPreview({ src }: { src?: string }) {
  if (!src) {
    return <p>视频生成后将在这里预览。</p>;
  }

  return <video src={src} controls playsInline />;
}
