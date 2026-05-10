# Homepage Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把首页升级成接近参考图的三栏工作台，并将时长、分镜数量、字幕开关和音色等核心参数真实接入前后端与 LangGraph 工作流。

**Architecture:** 先扩展 FastAPI 请求模型、任务对象和 `WorkflowState`，让参数链路完整贯通；再扩展前端类型与组件，最后重构首页为三栏工作台并补任务详情展示。视觉层建立在真实参数可提交、可查看、可回归测试的基础上。

**Tech Stack:** Next.js 15, React 19, Vitest, FastAPI, Pydantic, LangGraph, Ruff, MyPy

---

## File Structure

- Modify: `backend/app/core/models.py` - 扩展 API 请求/响应模型
- Modify: `backend/app/services/job_service.py` - 保存新增任务参数并注入工作流
- Modify: `backend/app/workflows/state.py` - 扩展工作流状态字段
- Modify: `backend/app/agents/director.py` - 读取时长约束
- Modify: `backend/app/agents/script.py` - 读取时长约束
- Modify: `backend/app/agents/storyboard.py` - 读取分镜数量
- Modify: `backend/app/agents/editor.py` - 读取字幕开关
- Modify: `backend/tests/test_jobs_api.py` - API 请求/响应新增字段测试
- Modify: `backend/tests/test_graph_flow.py` - 工作流状态新增字段测试
- Create: `frontend/src/components/generation-controls.tsx` - 首页中栏参数控制组件
- Create: `frontend/src/components/runtime-panel.tsx` - 首页右栏运行信息组件
- Modify: `frontend/src/components/job-form.tsx` - 与新布局配合并提交扩展 payload
- Modify: `frontend/src/app/page.tsx` - 首页改造成三栏工作台并组合各组件状态
- Modify: `frontend/src/app/jobs/[jobId]/page.tsx` - 展示本次生成参数
- Modify: `frontend/src/lib/types.ts` - 扩展前端类型
- Modify: `frontend/src/lib/api.ts` - 扩展创建任务 payload 与详情类型
- Modify: `frontend/src/__tests__/job-form.test.tsx` - 首页和表单行为回归
- Create: `frontend/src/__tests__/generation-controls.test.tsx` - 参数组件测试

### Task 1: 打通后端请求模型与任务数据

**Files:**
- Modify: `backend/app/core/models.py`
- Modify: `backend/app/services/job_service.py`
- Modify: `backend/tests/test_jobs_api.py`

- [ ] **Step 1: 写后端 API 失败测试，先定义新增字段契约**

```python
def test_create_job_persists_generation_controls() -> None:
    response = client.post(
        "/api/jobs",
        json={
            "topic": "时间管理",
            "style": "励志",
            "voice": "Chelsie",
            "duration": 60,
            "shotCount": 7,
            "subtitlesEnabled": False,
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "pending"

    job_id = response.json()["job_id"]
    detail_response = client.get(f"/api/jobs/{job_id}")

    assert detail_response.status_code == 200
    assert detail_response.json()["duration"] == 60
    assert detail_response.json()["shotCount"] == 7
    assert detail_response.json()["subtitlesEnabled"] is False
    assert detail_response.json()["aspectRatio"] == "9:16"
    assert detail_response.json()["voiceSelection"] == "Chelsie"
```

- [ ] **Step 2: 运行单测并确认按预期失败**

Run: `python -m pytest backend/tests/test_jobs_api.py::test_create_job_persists_generation_controls -q`  
Expected: FAIL，提示响应不包含 `duration`、`shotCount` 或请求模型不接受新字段

- [ ] **Step 3: 最小实现请求模型与任务对象字段**

```python
class CreateJobRequest(BaseModel):
    topic: str
    style: str
    voice: str = "auto"
    duration: Literal[15, 30, 60] = 30
    shotCount: Literal[3, 5, 7] = 5
    subtitlesEnabled: bool = True


class JobResponse(BaseModel):
    job_id: str
    topic: str
    style: str
    voice: str
    duration: int
    shotCount: int
    subtitlesEnabled: bool
    aspectRatio: str
    status: str


class JobDetailResponse(BaseModel):
    jobId: str
    topic: str
    style: str
    voiceSelection: str = "auto"
    duration: int = 30
    shotCount: int = 5
    subtitlesEnabled: bool = True
    aspectRatio: str = "9:16"
    status: str
    stages: list[JobStageResponse]
    brief: str | None = None
    script: str | None = None
    storyboard: list[dict[str, str]] | None = None
    visualAssets: list[str] | None = None
    voiceAsset: str | None = None
    finalVideo: str | None = None
    errorMessage: str | None = None
```

```python
job = JobDetailResponse(
    jobId=job_id,
    topic=payload.topic,
    style=payload.style,
    voiceSelection=payload.voice,
    duration=payload.duration,
    shotCount=payload.shotCount,
    subtitlesEnabled=payload.subtitlesEnabled,
    aspectRatio="9:16",
    status="pending",
    stages=[
        JobStageResponse(key=stage["key"], label=stage["label"], status="pending")
        for stage in DEFAULT_STAGES
    ],
)
```

- [ ] **Step 4: 重跑单测确认通过**

Run: `python -m pytest backend/tests/test_jobs_api.py::test_create_job_persists_generation_controls -q`  
Expected: PASS

- [ ] **Step 5: 跑后端 API 文件全量测试**

Run: `python -m pytest backend/tests/test_jobs_api.py -q`  
Expected: PASS

- [ ] **Step 6: 提交后端模型改动**

```bash
git add backend/app/core/models.py backend/app/services/job_service.py backend/tests/test_jobs_api.py
git commit -m "feat: persist homepage generation controls"
```

### Task 2: 打通 WorkflowState 与 agent 读取

**Files:**
- Modify: `backend/app/workflows/state.py`
- Modify: `backend/app/services/job_service.py`
- Modify: `backend/app/agents/director.py`
- Modify: `backend/app/agents/script.py`
- Modify: `backend/app/agents/storyboard.py`
- Modify: `backend/app/agents/editor.py`
- Modify: `backend/tests/test_graph_flow.py`

- [ ] **Step 1: 写工作流失败测试，先锁定新增状态字段**

```python
def test_langgraph_workflow_preserves_generation_controls() -> None:
    graph = build_graph(Settings())

    result = graph.invoke(
        {
            "job_id": "graph-test",
            "topic": "高效晨间习惯",
            "style": "干货",
            "voice_selection": "auto",
            "duration": 15,
            "shot_count": 3,
            "subtitles_enabled": False,
            "aspect_ratio": "9:16",
            "stages": [],
            "brief": "",
            "script": "",
            "storyboard": [],
            "visual_assets": [],
            "voice_asset": "",
            "final_video": "",
            "final_status": "pending",
        }
    )

    assert result["duration"] == 15
    assert result["shot_count"] == 3
    assert result["subtitles_enabled"] is False
    assert result["aspect_ratio"] == "9:16"
    assert len(result["storyboard"]) == 3
```

- [ ] **Step 2: 运行单测并确认失败**

Run: `python -m pytest backend/tests/test_graph_flow.py::test_langgraph_workflow_preserves_generation_controls -q`  
Expected: FAIL，提示缺字段或 `storyboard` 数量不符合预期

- [ ] **Step 3: 最小实现工作流状态与节点读取**

```python
class WorkflowState(TypedDict):
    job_id: str
    topic: str
    style: str
    voice_selection: str
    duration: int
    shot_count: int
    subtitles_enabled: bool
    aspect_ratio: str
    stages: list[str]
    brief: str
    script: str
    storyboard: list[dict[str, str]]
    visual_assets: list[str]
    voice_asset: str
    final_video: str
    final_status: str
```

```python
workflow_result = self._workflow.invoke(
    {
        "job_id": job.jobId,
        "topic": job.topic,
        "style": job.style,
        "voice_selection": job.voiceSelection,
        "duration": job.duration,
        "shot_count": job.shotCount,
        "subtitles_enabled": job.subtitlesEnabled,
        "aspect_ratio": job.aspectRatio,
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
```

```python
shot_total = state["shot_count"]
storyboard = [
    {"shot": str(index + 1), "caption": f"{state['style']}镜头 {index + 1}"}
    for index in range(shot_total)
]
```

- [ ] **Step 4: 重跑单测确认通过**

Run: `python -m pytest backend/tests/test_graph_flow.py::test_langgraph_workflow_preserves_generation_controls -q`  
Expected: PASS

- [ ] **Step 5: 跑后端工作流全量测试**

Run: `python -m pytest backend/tests/test_graph_flow.py -q`  
Expected: PASS

- [ ] **Step 6: 提交工作流改动**

```bash
git add backend/app/workflows/state.py backend/app/services/job_service.py backend/app/agents/director.py backend/app/agents/script.py backend/app/agents/storyboard.py backend/app/agents/editor.py backend/tests/test_graph_flow.py
git commit -m "feat: wire generation controls into workflow state"
```

### Task 3: 扩展前端类型与创建任务 payload

**Files:**
- Modify: `frontend/src/lib/types.ts`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/job-form.tsx`
- Modify: `frontend/src/__tests__/job-form.test.tsx`

- [ ] **Step 1: 写前端失败测试，锁定新增 payload**

```tsx
it("submits generation controls from the home page", async () => {
  vi.mocked(createJob).mockResolvedValue({
    job_id: "job-123",
    topic: "春节旅行攻略",
    style: "轻松口播",
    status: "pending",
  });

  render(<HomePage />);

  fireEvent.change(screen.getByLabelText("主题"), {
    target: { value: "春节旅行攻略" },
  });
  fireEvent.change(screen.getByLabelText("风格"), {
    target: { value: "轻松口播" },
  });
  fireEvent.click(screen.getByRole("button", { name: "60s" }));
  fireEvent.click(screen.getByRole("button", { name: "7 镜头" }));
  fireEvent.click(screen.getByRole("switch", { name: "字幕" }));
  fireEvent.click(screen.getByRole("button", { name: "开始生成" }));

  await waitFor(() => {
    expect(createJob).toHaveBeenCalledWith({
      topic: "春节旅行攻略",
      style: "轻松口播",
      voice: "auto",
      duration: 60,
      shotCount: 7,
      subtitlesEnabled: false,
    });
  });
});
```

- [ ] **Step 2: 运行前端单测并确认失败**

Run: `npm test -- --run frontend/src/__tests__/job-form.test.tsx`  
Expected: FAIL，提示缺少新控件或 payload 不包含新字段

- [ ] **Step 3: 最小实现类型与表单提交流程**

```ts
export type CreateJobInput = {
  topic: string;
  style: string;
  voice: string;
  duration: 15 | 30 | 60;
  shotCount: 3 | 5 | 7;
  subtitlesEnabled: boolean;
};

export type JobDetail = {
  jobId: string;
  topic: string;
  style: string;
  voiceSelection: string;
  duration: number;
  shotCount: number;
  subtitlesEnabled: boolean;
  aspectRatio: string;
  status: JobStatus;
  stages: JobStage[];
  brief?: string | null;
  script?: string | null;
  storyboard?: Array<{ shot: string; caption: string }> | null;
  visualAssets?: string[] | null;
  voiceAsset?: string | null;
  finalVideo?: string | null;
  errorMessage?: string | null;
};
```

```tsx
onSubmit?.({
  topic,
  style,
  voice,
  duration,
  shotCount,
  subtitlesEnabled,
});
```

- [ ] **Step 4: 重跑前端单测确认通过**

Run: `npm test -- --run frontend/src/__tests__/job-form.test.tsx`  
Expected: PASS

- [ ] **Step 5: 提交类型与 payload 改动**

```bash
git add frontend/src/lib/types.ts frontend/src/lib/api.ts frontend/src/components/job-form.tsx frontend/src/__tests__/job-form.test.tsx
git commit -m "feat: extend homepage payload with generation controls"
```

### Task 4: 实现 GenerationControls 与 RuntimePanel

**Files:**
- Create: `frontend/src/components/generation-controls.tsx`
- Create: `frontend/src/components/runtime-panel.tsx`
- Create: `frontend/src/__tests__/generation-controls.test.tsx`

- [ ] **Step 1: 写参数组件失败测试**

```tsx
it("renders duration, shot count, aspect ratio, and subtitles controls", () => {
  render(
    <GenerationControls
      duration={30}
      shotCount={5}
      subtitlesEnabled
      onDurationChange={vi.fn()}
      onShotCountChange={vi.fn()}
      onSubtitlesEnabledChange={vi.fn()}
    />
  );

  expect(screen.getByText("视频基础参数")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "15s" })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "30s" })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByText("9:16 竖屏")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "5 镜头" })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByRole("switch", { name: "字幕" })).toBeChecked();
});
```

- [ ] **Step 2: 运行单测并确认失败**

Run: `npm test -- --run frontend/src/__tests__/generation-controls.test.tsx`  
Expected: FAIL，提示组件文件不存在

- [ ] **Step 3: 最小实现两个新组件**

```tsx
export function GenerationControls(props: GenerationControlsProps) {
  return (
    <section aria-label="视频基础参数">
      <h2>视频基础参数</h2>
      <div>
        {([15, 30, 60] as const).map((value) => (
          <button
            key={value}
            type="button"
            aria-pressed={props.duration === value}
            onClick={() => props.onDurationChange(value)}
          >
            {value}s
          </button>
        ))}
      </div>
      <p>9:16 竖屏</p>
      <div>
        {([3, 5, 7] as const).map((value) => (
          <button
            key={value}
            type="button"
            aria-pressed={props.shotCount === value}
            onClick={() => props.onShotCountChange(value)}
          >
            {value} 镜头
          </button>
        ))}
      </div>
      <label>
        <input
          aria-label="字幕"
          type="checkbox"
          role="switch"
          checked={props.subtitlesEnabled}
          onChange={(event) => props.onSubtitlesEnabledChange(event.target.checked)}
        />
        字幕
      </label>
    </section>
  );
}
```

```tsx
export function RuntimePanel({ voiceCatalog }: RuntimePanelProps) {
  return (
    <aside aria-label="运行状态">
      <h2>运行状态</h2>
      <p>当前音色目录：{voiceCatalog ? `${voiceCatalog.provider} / ${voiceCatalog.model}` : "加载中"}</p>
      <p>真实出片需要 provider 与 ffmpeg 均已就绪。</p>
      <p>生成完成后，可从任务详情页查看素材、配音和成片结果。</p>
    </aside>
  );
}
```

- [ ] **Step 4: 重跑单测确认通过**

Run: `npm test -- --run frontend/src/__tests__/generation-controls.test.tsx`  
Expected: PASS

- [ ] **Step 5: 提交新组件改动**

```bash
git add frontend/src/components/generation-controls.tsx frontend/src/components/runtime-panel.tsx frontend/src/__tests__/generation-controls.test.tsx
git commit -m "feat: add homepage workbench control panels"
```

### Task 5: 改造首页为三栏工作台

**Files:**
- Modify: `frontend/src/app/page.tsx`
- Modify: `frontend/src/components/job-form.tsx`
- Modify: `frontend/src/__tests__/job-form.test.tsx`

- [ ] **Step 1: 写首页布局失败测试**

```tsx
it("renders the homepage workbench layout", async () => {
  render(<HomePage />);

  await waitFor(() => {
    expect(screen.getByText("AI 短视频工作台")).toBeInTheDocument();
  });

  expect(screen.getByText("视频基础参数")).toBeInTheDocument();
  expect(screen.getByText("运行状态")).toBeInTheDocument();
  expect(screen.getByText("当前音色目录：qwen / qwen3-tts-flash")).toBeInTheDocument();
});
```

- [ ] **Step 2: 运行首页测试并确认失败**

Run: `npm test -- --run frontend/src/__tests__/job-form.test.tsx`  
Expected: FAIL，提示新布局关键文案不存在

- [ ] **Step 3: 最小实现三栏工作台布局**

```tsx
return (
  <main className="workbench">
    <section className="workbench__intro">
      <p className="eyebrow">Pixelle-style Studio</p>
      <h1>AI 短视频工作台</h1>
      <p>输入主题与风格，配置核心参数后生成中文短视频。</p>
      <JobForm
        onSubmit={handleSubmit}
        voiceOptions={voiceCatalog?.voices}
        duration={duration}
        shotCount={shotCount}
        subtitlesEnabled={subtitlesEnabled}
      />
      {submitError ? <p role="alert">{submitError}</p> : null}
    </section>
    <GenerationControls
      duration={duration}
      shotCount={shotCount}
      subtitlesEnabled={subtitlesEnabled}
      onDurationChange={setDuration}
      onShotCountChange={setShotCount}
      onSubtitlesEnabledChange={setSubtitlesEnabled}
    />
    <RuntimePanel voiceCatalog={voiceCatalog} />
  </main>
);
```

- [ ] **Step 4: 重跑首页测试确认通过**

Run: `npm test -- --run frontend/src/__tests__/job-form.test.tsx`  
Expected: PASS

- [ ] **Step 5: 跑前端全量测试并确认通过**

Run: `npm test`  
Expected: PASS

- [ ] **Step 6: 提交首页工作台改动**

```bash
git add frontend/src/app/page.tsx frontend/src/components/job-form.tsx frontend/src/__tests__/job-form.test.tsx
git commit -m "feat: redesign homepage as workbench"
```

### Task 6: 扩展任务详情并完成全量验证

**Files:**
- Modify: `frontend/src/app/jobs/[jobId]/page.tsx`
- Modify: `backend/tests/test_jobs_api.py`
- Modify: `frontend/src/lib/types.ts`

- [ ] **Step 1: 补任务详情失败测试或断言**

```python
assert detail_response.json()["duration"] == 60
assert detail_response.json()["shotCount"] == 7
assert detail_response.json()["subtitlesEnabled"] is False
assert detail_response.json()["aspectRatio"] == "9:16"
```

```tsx
<p>时长：{job.duration}s</p>
<p>分镜数量：{job.shotCount}</p>
<p>字幕：{job.subtitlesEnabled ? "开启" : "关闭"}</p>
<p>画幅：{job.aspectRatio}</p>
```

- [ ] **Step 2: 运行相关测试确认失败**

Run: `python -m pytest backend/tests/test_jobs_api.py -q`  
Expected: FAIL，若详情结构尚未完整展示

- [ ] **Step 3: 最小实现详情页参数展示**

```tsx
<section>
  <h2>生成参数</h2>
  <p>音色：{job.voiceSelection}</p>
  <p>时长：{job.duration}s</p>
  <p>分镜数量：{job.shotCount}</p>
  <p>字幕：{job.subtitlesEnabled ? "开启" : "关闭"}</p>
  <p>画幅：{job.aspectRatio}</p>
</section>
```

- [ ] **Step 4: 跑全量验证**

Run: `python -m pytest backend/tests -q`  
Expected: PASS

Run: `python -m ruff check backend`  
Expected: PASS

Run: `python -m mypy app`  
Expected: PASS

Run: `npm test`  
Expected: PASS

Run: `npm run build`  
Expected: PASS

- [ ] **Step 5: 提交收尾改动**

```bash
git add frontend/src/app/jobs/[jobId]/page.tsx frontend/src/lib/types.ts backend/tests/test_jobs_api.py
git commit -m "feat: surface generation controls in job details"
```
