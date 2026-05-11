import React from "react";

export function VideoPreview({
  src,
  className,
}: {
  src?: string;
  className?: string;
}) {
  if (!src) {
    return <p>视频生成后将在这里预览。</p>;
  }

  if (/^https?:\/\//.test(src) || /^[A-Za-z]:\\/.test(src) || src.startsWith("/")) {
    return (
      <div className={`media-frame${className ? ` ${className}` : ""}`}>
        <video className="preview-video" src={src} controls playsInline preload="metadata" />
      </div>
    );
  }

  return <p>成片路径：{src}</p>;
}
