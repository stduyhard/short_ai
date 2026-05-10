# short_video

一个用于构建前后端分离 AI 短视频生成系统的项目仓库。

## 目录

- `frontend`: Next.js 前端，提供任务创建与结果查看页面
- `backend`: Python 后端，提供任务与工作流 API
- `scripts`: 本地开发与辅助脚本
- `docs`: 设计与规划文档

## 开发目标

目标是让用户输入主题和风格后，系统自动生成中文竖屏短视频。

## 本地开发前提

- Python 3.11+
- Node.js 20+
- `backend` 依赖已安装
- `frontend` 依赖已安装

## 后端本地开发

在仓库根目录执行：

```powershell
Set-Location .\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

后端健康检查地址：

```text
http://127.0.0.1:8000/health
```

后端测试命令：

```powershell
python -m pytest backend/tests
```

## 前端本地开发

前端默认访问 `http://127.0.0.1:8000`，也可以通过 `NEXT_PUBLIC_API_BASE_URL` 覆盖。

在仓库根目录执行：

```powershell
Set-Location .\frontend
$env:NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:8000"
npm run dev -- --hostname 127.0.0.1 --port 3000
```

前端测试命令：

```powershell
Set-Location .\frontend
npm test
```

## 一键本地联调

仓库提供了最小联调脚本 [`scripts/dev.ps1`](D:\short_video\scripts\dev.ps1)：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1
```

这个脚本会：

- 在新 PowerShell 窗口启动后端 `uvicorn`
- 在当前窗口启动前端 `next dev`
- 为前端自动设置 `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`

如需修改端口，可以传参：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1 -BackendPort 8001 -FrontendPort 3001
```

## 真实出片准备

要走真实 `OpenAI + ffmpeg` 出片链路，当前项目至少需要满足这两项：

- 设置 `OPENAI_API_KEY`
- 安装 `ffmpeg`，或把 `FFMPEG_BINARY` 指向现有可执行文件

PowerShell 示例：

```powershell
$env:OPENAI_API_KEY = "sk-..."
$env:FFMPEG_BINARY = "ffmpeg"
```

如果你已经启动了后端，可以直接检查运行时就绪度：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/runtime/readiness
```

也可以使用仓库自带脚本做本地检查：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-real-generation-readiness.ps1
```

当返回里这三个值都满足时，就可以继续做第一次真实出片验证：

- `openaiConfigured = true`
- `ffmpegAvailable = true`
- `readyForRealGeneration = true`

一个最小验证流程是：

1. 启动后端 `uvicorn`
2. 启动前端或直接调用创建任务接口
3. `POST /api/jobs`
4. `POST /api/jobs/{jobId}/run`
5. `GET /api/jobs/{jobId}` 查看 `status`、`voiceAsset`、`finalVideo`

如果当前环境还没装好，后端会返回 `degraded`，这表示工作流已跑通，但真实成片依赖还未满足。

## 验收命令

按 Task 10 的本地验收方式，在仓库根目录执行：

```powershell
python -m pytest backend/tests
Set-Location .\frontend
npm test
```

如需把联调脚本本身也纳入验收，补充执行：

```powershell
$tokens = $null
$errors = $null
[void][System.Management.Automation.Language.Parser]::ParseFile('D:\short_video\scripts\dev.ps1', [ref]$tokens, [ref]$errors)
if ($errors.Count -gt 0) { exit 1 }
```
