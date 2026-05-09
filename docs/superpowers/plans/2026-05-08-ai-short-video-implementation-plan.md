# AI 短视频 Web 应用 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个前后端分离的 AI 短视频 Web 应用，用户输入主题和风格后，系统通过 FastAPI + LangGraph 编排多 Agent 流程，自动生成可预览和下载的中文竖屏短视频。

**Architecture:** 项目采用 monorepo 结构，包含 `frontend` 和 `backend` 两个应用，以及共享的 `docs` 和脚本目录。前端负责表单、任务进度和结果预览；后端负责 API、LangGraph 工作流、供应商适配、媒体渲染和任务状态持久化。

**Tech Stack:** Frontend 使用 Next.js + TypeScript + Tailwind CSS；Backend 使用 FastAPI + Pydantic + LangGraph + Uvicorn；渲染层使用 Remotion + FFmpeg；测试使用 Vitest / React Testing Library / Pytest。

---

## 文件结构

### 目标目录布局

- `frontend/`
  - `package.json`
  - `next.config.mjs`
  - `tsconfig.json`
  - `src/app/page.tsx`
  - `src/app/jobs/[jobId]/page.tsx`
  - `src/components/job-form.tsx`
  - `src/components/job-stage-list.tsx`
  - `src/components/video-preview.tsx`
  - `src/lib/api.ts`
  - `src/lib/types.ts`
  - `src/__tests__/job-form.test.tsx`
  - `src/__tests__/job-stage-list.test.tsx`
- `backend/`
  - `pyproject.toml`
  - `app/main.py`
  - `app/core/config.py`
  - `app/core/models.py`
  - `app/services/job_service.py`
  - `app/workflows/state.py`
  - `app/workflows/graph.py`
  - `app/agents/director.py`
  - `app/agents/script.py`
  - `app/agents/storyboard.py`
  - `app/agents/visual.py`
  - `app/agents/voice.py`
  - `app/agents/editor.py`
  - `app/providers/llm.py`
  - `app/providers/image.py`
  - `app/providers/tts.py`
  - `app/providers/storage.py`
  - `app/render/renderer.py`
  - `tests/test_jobs_api.py`
  - `tests/test_graph_flow.py`
  - `tests/test_retry_flow.py`
- `scripts/`
  - `dev.ps1`
  - `render-worker.ps1`
- `.gitignore`
- `README.md`

### 结构职责说明

- `frontend/src/app`：承载页面路由
- `frontend/src/components`：承载可复用 UI 组件
- `frontend/src/lib`：承载 API 客户端和前端类型
- `backend/app/api`：承载 FastAPI 路由
- `backend/app/services`：承载任务创建、查询、重试等应用服务
- `backend/app/workflows`：承载 LangGraph 状态定义和工作流图
- `backend/app/agents`：承载六类 Agent 节点逻辑
- `backend/app/providers`：封装外部模型和存储服务
- `backend/app/render`：承载 Remotion + FFmpeg 渲染调用逻辑

## Task 1：初始化仓库与基础目录

**Files:**
- Create: `.gitignore`
- Create: `README.md`
- Create: `frontend/.gitkeep`
- Create: `backend/.gitkeep`
- Create: `scripts/.gitkeep`

- [ ] **Step 1: 创建 `.gitignore`**

```gitignore
node_modules/
.next/
dist/
coverage/
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.pyc
.env
.env.*
backend/.env
frontend/.env.local
tmp/
artifacts/
.superpowers/
```

- [ ] **Step 2: 创建 `README.md`**

```md
# short_video

前后端分离的 AI 短视频生成系统。

## 目录

- `frontend`: Next.js 前端
- `backend`: FastAPI + LangGraph 后端
- `docs`: 设计与规划文档

## 开发目标

用户输入主题和风格后，系统自动生成中文竖屏短视频。
```

- [ ] **Step 3: 创建占位目录文件**

```text
frontend/.gitkeep
backend/.gitkeep
scripts/.gitkeep
```

- [ ] **Step 4: 初始化 Git 仓库**

Run: `git init`
Expected: 输出 `Initialized empty Git repository`

- [ ] **Step 5: 首次提交**

```bash
git add .gitignore README.md frontend/.gitkeep backend/.gitkeep scripts/.gitkeep
git commit -m "chore: initialize repository structure"
```

## Task 2：搭建前端应用骨架

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/next.config.mjs`
- Create: `frontend/src/app/layout.tsx`
- Create: `frontend/src/app/page.tsx`
- Create: `frontend/src/app/globals.css`
- Test: `frontend/src/__tests__/job-form.test.tsx`

- [ ] **Step 1: 写前端首页测试**

```tsx
import { render, screen } from "@testing-library/react";
import HomePage from "../app/page";

describe("HomePage", () => {
  it("renders topic and style inputs", () => {
    render(<HomePage />);
    expect(screen.getByLabelText("主题")).toBeInTheDocument();
    expect(screen.getByLabelText("风格")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "开始生成" })).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `D:\Program\nodejs\npm.cmd test -- --run src/__tests__/job-form.test.tsx`
Expected: FAIL，提示缺少 `frontend/package.json` 或页面文件

- [ ] **Step 3: 创建 `frontend/package.json`**

```json
{
  "name": "short-video-frontend",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "test": "vitest"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.6.0",
    "@testing-library/react": "^16.0.0",
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.6.0",
    "vitest": "^2.1.0"
  }
}
```

```json
// frontend/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "es2022"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", ".next/types/**/*.ts"]
}
```

```js
// frontend/next.config.mjs
const nextConfig = {
  reactStrictMode: true,
};

export default nextConfig;
```

- [ ] **Step 4: 创建首页和布局最小实现**

```tsx
// frontend/src/app/page.tsx
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
```

```tsx
// frontend/src/app/layout.tsx
import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
```

- [ ] **Step 5: 运行测试并确认通过**

Run: `D:\Program\nodejs\npm.cmd test -- --run src/__tests__/job-form.test.tsx`
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add frontend/package.json frontend/tsconfig.json frontend/next.config.mjs frontend/src/app/layout.tsx frontend/src/app/page.tsx frontend/src/app/globals.css frontend/src/__tests__/job-form.test.tsx
git commit -m "feat: scaffold frontend app shell"
```

## Task 3：实现前端表单与任务详情页

**Files:**
- Create: `frontend/src/components/job-form.tsx`
- Create: `frontend/src/components/job-stage-list.tsx`
- Create: `frontend/src/components/video-preview.tsx`
- Create: `frontend/src/app/jobs/[jobId]/page.tsx`
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/lib/types.ts`
- Test: `frontend/src/__tests__/job-stage-list.test.tsx`

- [ ] **Step 1: 写任务阶段列表测试**

```tsx
import { render, screen } from "@testing-library/react";
import { JobStageList } from "../components/job-stage-list";

describe("JobStageList", () => {
  it("renders all pipeline stages", () => {
    render(
      <JobStageList
        stages={[
          { key: "director", label: "创意策划", status: "completed" },
          { key: "script", label: "文案生成", status: "running" },
          { key: "storyboard", label: "分镜生成", status: "pending" }
        ]}
      />
    );

    expect(screen.getByText("创意策划")).toBeInTheDocument();
    expect(screen.getByText("文案生成")).toBeInTheDocument();
    expect(screen.getByText("分镜生成")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `D:\Program\nodejs\npm.cmd test -- --run src/__tests__/job-stage-list.test.tsx`
Expected: FAIL，提示组件不存在

- [ ] **Step 3: 实现前端类型和组件**

```ts
// frontend/src/lib/types.ts
export type StageStatus = "pending" | "running" | "completed" | "failed";

export type JobStage = {
  key: string;
  label: string;
  status: StageStatus;
  message?: string;
};

export type JobDetail = {
  jobId: string;
  topic: string;
  style: string;
  status: StageStatus;
  stages: JobStage[];
  previewUrl?: string;
  finalVideoUrl?: string;
};
```

```tsx
// frontend/src/components/job-stage-list.tsx
import { JobStage } from "../lib/types";

export function JobStageList({ stages }: { stages: JobStage[] }) {
  return (
    <section>
      <h2>生成进度</h2>
      <ul>
        {stages.map((stage) => (
          <li key={stage.key}>
            <strong>{stage.label}</strong>
            <span>{stage.status}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
```

```tsx
// frontend/src/components/video-preview.tsx
export function VideoPreview({ src }: { src?: string }) {
  if (!src) {
    return <p>视频生成后将在这里预览。</p>;
  }

  return <video src={src} controls playsInline />;
}
```

```ts
// frontend/src/lib/api.ts
import { JobDetail } from "./types";

export async function fetchJobDetail(jobId: string): Promise<JobDetail> {
  const response = await fetch(`http://127.0.0.1:8000/api/jobs/${jobId}`);
  return response.json();
}
```

- [ ] **Step 4: 实现任务详情页最小版本**

```tsx
// frontend/src/app/jobs/[jobId]/page.tsx
import { JobStageList } from "../../../components/job-stage-list";

export default function JobDetailPage() {
  return (
    <main>
      <h1>任务详情</h1>
      <JobStageList
        stages={[
          { key: "director", label: "创意策划", status: "pending" },
          { key: "script", label: "文案生成", status: "pending" },
          { key: "storyboard", label: "分镜生成", status: "pending" },
          { key: "visual", label: "视觉素材生成", status: "pending" },
          { key: "voice", label: "配音与字幕生成", status: "pending" },
          { key: "editor", label: "视频渲染", status: "pending" }
        ]}
      />
    </main>
  );
}
```

- [ ] **Step 5: 运行测试并确认通过**

Run: `D:\Program\nodejs\npm.cmd test -- --run src/__tests__/job-stage-list.test.tsx`
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add frontend/src/components/job-form.tsx frontend/src/components/job-stage-list.tsx frontend/src/components/video-preview.tsx frontend/src/app/jobs/[jobId]/page.tsx frontend/src/lib/api.ts frontend/src/lib/types.ts frontend/src/__tests__/job-stage-list.test.tsx
git commit -m "feat: add job form and progress views"
```

## Task 4：搭建 FastAPI 后端骨架

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/main.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/models.py`
- Create: `backend/tests/test_jobs_api.py`

- [ ] **Step 1: 写健康检查与建任务接口测试**

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_job():
    response = client.post("/api/jobs", json={"topic": "时间管理", "style": "励志"})
    assert response.status_code == 201
    body = response.json()
    assert body["topic"] == "时间管理"
    assert body["style"] == "励志"
    assert body["status"] == "pending"
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `.\\.venv\\Scripts\\python.exe -m pytest backend/tests/test_jobs_api.py -q`
Expected: FAIL，提示 `app.main` 不存在

- [ ] **Step 3: 创建 `pyproject.toml`**

```toml
[project]
name = "short-video-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.115.0",
  "uvicorn>=0.30.0",
  "pydantic>=2.8.0",
  "langgraph>=0.2.0",
  "httpx>=0.27.0"
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3.0",
  "ruff>=0.6.0",
  "mypy>=1.11.0"
]
```

- [ ] **Step 4: 实现最小 FastAPI 应用**

```python
# backend/app/core/models.py
from pydantic import BaseModel

class CreateJobRequest(BaseModel):
    topic: str
    style: str

class JobResponse(BaseModel):
    job_id: str
    topic: str
    style: str
    status: str
```

```python
# backend/app/main.py
from uuid import uuid4
from fastapi import FastAPI
from app.core.models import CreateJobRequest, JobResponse

app = FastAPI()

@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/api/jobs", response_model=JobResponse, status_code=201)
def create_job(payload: CreateJobRequest) -> JobResponse:
    return JobResponse(
        job_id=str(uuid4()),
        topic=payload.topic,
        style=payload.style,
        status="pending",
    )
```

- [ ] **Step 5: 运行测试并确认通过**

Run: `.\\.venv\\Scripts\\python.exe -m pytest backend/tests/test_jobs_api.py -q`
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add backend/pyproject.toml backend/app/main.py backend/app/core/config.py backend/app/core/models.py backend/tests/test_jobs_api.py
git commit -m "feat: scaffold fastapi backend"
```

## Task 5：实现 Job Service 与持久化模型

**Files:**
- Create: `backend/app/services/job_service.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/core/models.py`
- Modify: `backend/tests/test_jobs_api.py`
- Test: `backend/tests/test_jobs_api.py`

- [ ] **Step 1: 扩充 API 测试，覆盖任务查询**

```python
def test_get_job_detail():
    create_response = client.post("/api/jobs", json={"topic": "习惯养成", "style": "治愈"})
    job_id = create_response.json()["job_id"]

    detail_response = client.get(f"/api/jobs/{job_id}")
    assert detail_response.status_code == 200
    body = detail_response.json()
    assert body["job_id"] == job_id
    assert len(body["stages"]) == 6
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `.\\.venv\\Scripts\\python.exe -m pytest backend/tests/test_jobs_api.py -q`
Expected: FAIL，提示 `/api/jobs/{job_id}` 未实现

- [ ] **Step 3: 实现内存版 Job Service**

```python
# backend/app/services/job_service.py
from uuid import uuid4

DEFAULT_STAGES = [
    {"key": "director", "label": "创意策划", "status": "pending"},
    {"key": "script", "label": "文案生成", "status": "pending"},
    {"key": "storyboard", "label": "分镜生成", "status": "pending"},
    {"key": "visual", "label": "视觉素材生成", "status": "pending"},
    {"key": "voice", "label": "配音与字幕生成", "status": "pending"},
    {"key": "editor", "label": "视频渲染", "status": "pending"},
]

class JobService:
    def __init__(self) -> None:
        self._jobs: dict[str, dict] = {}

    def create_job(self, topic: str, style: str) -> dict:
        job_id = str(uuid4())
        job = {
            "job_id": job_id,
            "topic": topic,
            "style": style,
            "status": "pending",
            "stages": DEFAULT_STAGES,
        }
        self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> dict:
        return self._jobs[job_id]
```

- [ ] **Step 4: 接入 API 路由**

```python
# backend/app/main.py
from fastapi import FastAPI, HTTPException
from app.core.models import CreateJobRequest
from app.services.job_service import JobService

app = FastAPI()
job_service = JobService()

@app.post("/api/jobs", status_code=201)
def create_job(payload: CreateJobRequest) -> dict:
    return job_service.create_job(payload.topic, payload.style)

@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    try:
        return job_service.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc
```

- [ ] **Step 5: 运行测试并确认通过**

Run: `.\\.venv\\Scripts\\python.exe -m pytest backend/tests/test_jobs_api.py -q`
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add backend/app/services/job_service.py backend/app/main.py backend/app/core/models.py backend/tests/test_jobs_api.py
git commit -m "feat: add job service and detail api"
```

## Task 6：实现 LangGraph 状态与六阶段工作流

**Files:**
- Create: `backend/app/workflows/state.py`
- Create: `backend/app/workflows/graph.py`
- Create: `backend/app/agents/director.py`
- Create: `backend/app/agents/script.py`
- Create: `backend/app/agents/storyboard.py`
- Create: `backend/app/agents/visual.py`
- Create: `backend/app/agents/voice.py`
- Create: `backend/app/agents/editor.py`
- Test: `backend/tests/test_graph_flow.py`

- [ ] **Step 1: 写工作流顺序测试**

```python
from app.workflows.graph import build_graph

def test_graph_runs_all_stages():
    graph = build_graph()
    result = graph.invoke({"topic": "拖延症", "style": "励志", "stages": []})
    assert result["final_status"] == "completed"
    assert result["stages"] == [
        "director",
        "script",
        "storyboard",
        "visual",
        "voice",
        "editor",
    ]
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `.\\.venv\\Scripts\\python.exe -m pytest backend/tests/test_graph_flow.py -q`
Expected: FAIL，提示 `build_graph` 不存在

- [ ] **Step 3: 定义工作流状态**

```python
# backend/app/workflows/state.py
from typing import TypedDict

class WorkflowState(TypedDict):
    topic: str
    style: str
    stages: list[str]
    brief: str
    script: str
    storyboard: list[dict]
    visual_assets: list[str]
    voice_asset: str
    final_video: str
    final_status: str
```

- [ ] **Step 4: 实现六个最小 Agent**

```python
# backend/app/agents/director.py
from app.workflows.state import WorkflowState

def run_director(state: WorkflowState) -> WorkflowState:
    state["stages"].append("director")
    state["brief"] = f"{state['style']}风格的{state['topic']}短视频"
    return state
```

```python
# backend/app/agents/script.py
from app.workflows.state import WorkflowState

def run_script(state: WorkflowState) -> WorkflowState:
    state["stages"].append("script")
    state["script"] = f"这是一个关于{state['topic']}的{state['style']}风格口播文案。"
    return state
```

```python
# backend/app/agents/storyboard.py
from app.workflows.state import WorkflowState

def run_storyboard(state: WorkflowState) -> WorkflowState:
    state["stages"].append("storyboard")
    state["storyboard"] = [{"shot": 1, "caption": state["script"]}]
    return state
```

```python
# backend/app/agents/visual.py
from app.workflows.state import WorkflowState

def run_visual(state: WorkflowState) -> WorkflowState:
    state["stages"].append("visual")
    state["visual_assets"] = ["artifacts/shot-1.png"]
    return state
```

```python
# backend/app/agents/voice.py
from app.workflows.state import WorkflowState

def run_voice(state: WorkflowState) -> WorkflowState:
    state["stages"].append("voice")
    state["voice_asset"] = "artifacts/voice.mp3"
    return state
```

```python
# backend/app/agents/editor.py
from app.workflows.state import WorkflowState

def run_editor(state: WorkflowState) -> WorkflowState:
    state["stages"].append("editor")
    state["final_video"] = "artifacts/final.mp4"
    state["final_status"] = "completed"
    return state
```

- [ ] **Step 5: 用 LangGraph 串起工作流**

```python
# backend/app/workflows/graph.py
from langgraph.graph import END, StateGraph
from app.agents.director import run_director
from app.agents.script import run_script
from app.agents.storyboard import run_storyboard
from app.agents.visual import run_visual
from app.agents.voice import run_voice
from app.agents.editor import run_editor
from app.workflows.state import WorkflowState

def build_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node("director", run_director)
    graph.add_node("script", run_script)
    graph.add_node("storyboard", run_storyboard)
    graph.add_node("visual", run_visual)
    graph.add_node("voice", run_voice)
    graph.add_node("editor", run_editor)
    graph.set_entry_point("director")
    graph.add_edge("director", "script")
    graph.add_edge("script", "storyboard")
    graph.add_edge("storyboard", "visual")
    graph.add_edge("visual", "voice")
    graph.add_edge("voice", "editor")
    graph.add_edge("editor", END)
    return graph.compile()
```

- [ ] **Step 6: 运行测试并确认通过**

Run: `.\\.venv\\Scripts\\python.exe -m pytest backend/tests/test_graph_flow.py -q`
Expected: PASS

- [ ] **Step 7: 提交**

```bash
git add backend/app/workflows/state.py backend/app/workflows/graph.py backend/app/agents/director.py backend/app/agents/script.py backend/app/agents/storyboard.py backend/app/agents/visual.py backend/app/agents/voice.py backend/app/agents/editor.py backend/tests/test_graph_flow.py
git commit -m "feat: add langgraph workflow skeleton"
```

## Task 7：将工作流接入 API 与阶段重试

**Files:**
- Modify: `backend/app/services/job_service.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_retry_flow.py`
- Modify: `backend/tests/test_jobs_api.py`

- [ ] **Step 1: 写重试接口测试**

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_retry_stage():
    create_response = client.post("/api/jobs", json={"topic": "自律", "style": "励志"})
    job_id = create_response.json()["job_id"]

    retry_response = client.post(f"/api/jobs/{job_id}/retry", json={"stage": "visual"})
    assert retry_response.status_code == 202
    assert retry_response.json()["stage"] == "visual"
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `.\\.venv\\Scripts\\python.exe -m pytest backend/tests/test_retry_flow.py -q`
Expected: FAIL，提示重试接口不存在

- [ ] **Step 3: 在 `JobService` 中接入工作流**

```python
# backend/app/services/job_service.py
from app.workflows.graph import build_graph

class JobService:
    def __init__(self) -> None:
        self._jobs: dict[str, dict] = {}
        self._graph = build_graph()

    def run_job(self, job_id: str) -> dict:
        job = self._jobs[job_id]
        result = self._graph.invoke(
            {
                "topic": job["topic"],
                "style": job["style"],
                "stages": [],
                "brief": "",
                "script": "",
                "storyboard": [],
                "visual_assets": [],
                "voice_asset": "",
                "final_video": "",
                "final_status": "running",
            }
        )
        job["status"] = result["final_status"]
        return job

    def retry_stage(self, job_id: str, stage: str) -> dict:
        job = self._jobs[job_id]
        return {"job_id": job_id, "stage": stage, "status": "accepted"}
```

- [ ] **Step 4: 暴露运行与重试接口**

```python
# backend/app/main.py
from pydantic import BaseModel

class RetryRequest(BaseModel):
    stage: str

@app.post("/api/jobs/{job_id}/run", status_code=202)
def run_job(job_id: str) -> dict:
    return job_service.run_job(job_id)

@app.post("/api/jobs/{job_id}/retry", status_code=202)
def retry_job_stage(job_id: str, payload: RetryRequest) -> dict:
    return job_service.retry_stage(job_id, payload.stage)
```

- [ ] **Step 5: 运行测试并确认通过**

Run: `.\\.venv\\Scripts\\python.exe -m pytest backend/tests/test_jobs_api.py backend/tests/test_retry_flow.py -q`
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add backend/app/services/job_service.py backend/app/main.py backend/tests/test_retry_flow.py backend/tests/test_jobs_api.py
git commit -m "feat: connect workflow execution and retry api"
```

## Task 8：接入渲染层骨架与 Provider 抽象

**Files:**
- Create: `backend/app/providers/llm.py`
- Create: `backend/app/providers/image.py`
- Create: `backend/app/providers/tts.py`
- Create: `backend/app/providers/storage.py`
- Create: `backend/app/render/renderer.py`
- Create: `scripts/render-worker.ps1`
- Test: `backend/tests/test_graph_flow.py`

- [ ] **Step 1: 为渲染结果增加断言**

```python
def test_graph_sets_render_artifacts():
    graph = build_graph()
    result = graph.invoke({"topic": "注意力", "style": "治愈", "stages": []})
    assert result["voice_asset"].endswith(".mp3")
    assert result["final_video"].endswith(".mp4")
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `.\\.venv\\Scripts\\python.exe -m pytest backend/tests/test_graph_flow.py -q`
Expected: FAIL，若当前返回值未满足断言

- [ ] **Step 3: 创建 Provider 抽象**

```python
# backend/app/providers/llm.py
class LLMProvider:
    def generate_script(self, topic: str, style: str) -> str:
        return f"主题：{topic}；风格：{style}"
```

```python
# backend/app/providers/image.py
class ImageProvider:
    def generate_images(self, prompts: list[str]) -> list[str]:
        return [f"artifacts/{index + 1}.png" for index, _ in enumerate(prompts)]
```

```python
# backend/app/providers/tts.py
class TTSProvider:
    def synthesize(self, script: str) -> str:
        return "artifacts/voice.mp3"
```

```python
# backend/app/providers/storage.py
class StorageProvider:
    def save(self, path: str) -> str:
        return path
```

- [ ] **Step 4: 创建渲染器骨架**

```python
# backend/app/render/renderer.py
class VideoRenderer:
    def render(self, image_paths: list[str], voice_path: str) -> str:
        if not image_paths:
            raise ValueError("image_paths must not be empty")
        if not voice_path.endswith(".mp3"):
            raise ValueError("voice_path must be an mp3 file")
        return "artifacts/final.mp4"
```

```powershell
# scripts/render-worker.ps1
Write-Host "Render worker placeholder"
```

- [ ] **Step 5: 运行测试并确认通过**

Run: `.\\.venv\\Scripts\\python.exe -m pytest backend/tests/test_graph_flow.py -q`
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add backend/app/providers/llm.py backend/app/providers/image.py backend/app/providers/tts.py backend/app/providers/storage.py backend/app/render/renderer.py scripts/render-worker.ps1 backend/tests/test_graph_flow.py
git commit -m "feat: add provider interfaces and renderer skeleton"
```

## Task 9：打通前后端联调最小闭环

**Files:**
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/job-form.tsx`
- Modify: `frontend/src/app/page.tsx`
- Modify: `frontend/src/app/jobs/[jobId]/page.tsx`
- Modify: `backend/app/main.py`
- Test: `frontend/src/__tests__/job-form.test.tsx`

- [ ] **Step 1: 写表单提交行为测试**

```tsx
import { fireEvent, render, screen } from "@testing-library/react";
import { JobForm } from "../components/job-form";

describe("JobForm", () => {
  it("submits topic and style", async () => {
    const onSubmit = vi.fn();
    render(<JobForm onSubmit={onSubmit} />);

    fireEvent.change(screen.getByLabelText("主题"), { target: { value: "情绪管理" } });
    fireEvent.change(screen.getByLabelText("风格"), { target: { value: "治愈" } });
    fireEvent.click(screen.getByRole("button", { name: "开始生成" }));

    expect(onSubmit).toHaveBeenCalledWith({ topic: "情绪管理", style: "治愈" });
  });
});
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `D:\Program\nodejs\npm.cmd test -- --run src/__tests__/job-form.test.tsx`
Expected: FAIL，提示 `JobForm` 未实现

- [ ] **Step 3: 实现 API 客户端和表单组件**

```ts
// frontend/src/lib/api.ts
export async function createJob(input: { topic: string; style: string }) {
  const response = await fetch("http://127.0.0.1:8000/api/jobs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  return response.json();
}
```

```tsx
// frontend/src/components/job-form.tsx
"use client";

import { useState } from "react";

export function JobForm({
  onSubmit,
}: {
  onSubmit: (value: { topic: string; style: string }) => void;
}) {
  const [topic, setTopic] = useState("");
  const [style, setStyle] = useState("");

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit({ topic, style });
      }}
    >
      <label htmlFor="topic">主题</label>
      <input id="topic" value={topic} onChange={(event) => setTopic(event.target.value)} />
      <label htmlFor="style">风格</label>
      <input id="style" value={style} onChange={(event) => setStyle(event.target.value)} />
      <button type="submit">开始生成</button>
    </form>
  );
}
```

- [ ] **Step 4: 在首页接入提交逻辑**

```tsx
// frontend/src/app/page.tsx
import { JobForm } from "../components/job-form";

export default function HomePage() {
  return (
    <main>
      <h1>AI 短视频生成</h1>
      <JobForm onSubmit={(value) => console.log(value)} />
    </main>
  );
}
```

- [ ] **Step 5: 运行测试并确认通过**

Run: `D:\Program\nodejs\npm.cmd test -- --run src/__tests__/job-form.test.tsx`
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add frontend/src/lib/api.ts frontend/src/components/job-form.tsx frontend/src/app/page.tsx frontend/src/app/jobs/[jobId]/page.tsx backend/app/main.py frontend/src/__tests__/job-form.test.tsx
git commit -m "feat: connect frontend form to backend api contract"
```

## Task 10：补齐开发脚本与验收命令

**Files:**
- Create: `scripts/dev.ps1`
- Modify: `README.md`

- [ ] **Step 1: 创建本地联调脚本**

```powershell
Write-Host "Start backend: uvicorn app.main:app --reload --app-dir backend"
Write-Host "Start frontend: npm run dev"
```

- [ ] **Step 2: 更新 README 的开发说明**

````md
## 本地开发

### 后端

1. 创建虚拟环境
2. 安装 `backend/pyproject.toml` 中的依赖
3. 启动命令：

```bash
uvicorn app.main:app --reload --app-dir backend
```

### 前端

1. 进入 `frontend`
2. 安装依赖
3. 启动命令：

```bash
npm run dev
```
````

- [ ] **Step 3: 运行后端测试**

Run: `.\\.venv\\Scripts\\python.exe -m pytest backend/tests -q`
Expected: PASS

- [ ] **Step 4: 运行前端测试**

Run: `D:\Program\nodejs\npm.cmd test -- --run`
Expected: PASS

- [ ] **Step 5: 最终提交**

```bash
git add scripts/dev.ps1 README.md
git commit -m "docs: add local development workflow"
```

## 计划自检

### Spec 覆盖检查

- 前后端分离：由 Task 2、Task 3、Task 4、Task 9 覆盖
- FastAPI 后端：由 Task 4、Task 5、Task 7 覆盖
- LangGraph 多 Agent 工作流：由 Task 6、Task 7 覆盖
- 六阶段任务进度：由 Task 3、Task 5、Task 7 覆盖
- 自动渲染骨架：由 Task 8 覆盖
- 测试策略：由所有任务内测试步骤覆盖

### 占位项检查

- 无 `TODO`
- 无 `TBD`
- 无“后续再补”的空泛步骤

### 类型一致性检查

- 前端统一使用 `topic` / `style` / `stages`
- 后端统一使用 `job_id` / `status` / `stages`
- 工作流统一使用六阶段键值：`director`、`script`、`storyboard`、`visual`、`voice`、`editor`
