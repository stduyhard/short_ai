import React from "react";

export default function HomePage() {
  return (
    <main>
      <h1>AI 短视频生成</h1>
      <form>
        <label htmlFor="topic">主题</label>
        <input id="topic" name="topic" />
        <label htmlFor="style">风格</label>
        <input id="style" name="style" />
        <button type="submit">开始生成</button>
      </form>
    </main>
  );
}
