# AI 短视频工作台首页改造设计

## 背景

当前首页仍然是最小表单结构，只能完成主题、风格、音色的基础输入，整体形态更像开发期占位页面，不符合“AI 一键成片工作台”的产品预期。

这次改造的目标，是将首页升级为接近参考界面风格的三栏工作台，同时把一组最核心的视频生成参数真正接入前后端与工作流，而不是只做视觉占位。

参考方向：
- `Pixelle-Video` WebUI 截图的工作台式布局
- 浅色控制台风格
- 明确的分区、卡片化组织和生成状态可视化

## 目标

本次改造要同时满足两类目标：

1. 产品目标
- 让首页更像专业视频生成工作台，而不是普通表单页
- 把主要控制项集中到一个高可读、高密度但不拥挤的桌面端界面
- 让用户在点击生成前就清楚自己正在控制哪些结果参数

2. 工程目标
- 让新增控制项真正进入任务创建请求、任务数据和 LangGraph 工作流状态
- 保持与当前 `Next.js + FastAPI + LangGraph` 架构一致
- 为后续继续扩展更多控制项留出稳定接口

## 用户输入范围

本次首页将真正支持以下输入：

- `topic`：主题
- `style`：风格
- `voice`：音色，可选，默认自动匹配
- `duration`：时长，固定三档 `15 / 30 / 60`
- `shotCount`：分镜数量，固定三档 `3 / 5 / 7`
- `subtitlesEnabled`：字幕开关，布尔值

本次首页也会展示以下信息，但暂不开放复杂配置：

- `aspectRatio`：固定显示 `9:16`
- 当前音色目录来源：`TTS_PROVIDER / TTS_MODEL`
- 最近一次提交失败提示或运行入口提示

## 不在本次范围内

以下内容明确不纳入本次实现：

- 模型级高级参数配置
- 自定义秒数输入
- 多画幅切换
- 字幕样式与位置配置
- 时间线编辑器
- 多模板系统
- 完整复刻参考图中所有高级控制区
- 任务历史管理面板
- 移动端与桌面端完全等复杂度的布局

## 首页布局设计

首页改成三栏工作台布局：

1. 左栏：创作输入区
- 产品标题与一句价值说明
- `主题` 输入框
- `风格` 输入框
- `音色` 下拉框
- 主按钮：`开始生成`
- 提交错误提示

2. 中栏：生成参数区
- `视频基础参数` 卡片
- `时长` 选项卡：`15s / 30s / 60s`
- `画幅` 固定展示卡：`9:16 竖屏`
- `分镜数量` 选项卡：`3 / 5 / 7`
- `字幕开关`：开启 / 关闭
- 一段简短说明，提示这些参数会真正影响生成结果

3. 右栏：运行状态与结果入口区
- 当前音色目录来源
- 任务工作流状态说明
- 真实出片前提提示，例如 provider / ffmpeg 就绪性说明
- 最近一次生成结果入口或空状态占位

整体视觉方向：

- 浅色背景，不走暗黑风
- 使用大圆角卡片、分层阴影和更清晰的区块留白
- 桌面端以左右分栏突出“创作输入”“参数控制”“运行反馈”
- 移动端退化为纵向堆叠，但保留相同信息层次

## 前端实现设计

### 页面职责

首页页面负责：

- 加载音色目录
- 管理提交状态与提交错误
- 组装创建任务请求
- 呈现三栏工作台布局

首页不负责：

- 长任务轮询
- 任务运行
- 任务详情预览的复杂交互

### 组件拆分建议

- `HomePage`
  - 负责页面数据加载、提交与布局编排
- `JobForm`
  - 负责主题、风格、音色和提交按钮
- `GenerationControls`
  - 负责时长、画幅、分镜数量、字幕开关
- `RuntimePanel`
  - 负责音色目录、运行提示、结果入口占位

如果当前文件规模允许，也可以先只新增 `GenerationControls` 和 `RuntimePanel` 两个组件，避免首页文件过快膨胀。

### 前端状态

首页至少维护这些状态：

- `submitError`
- `voiceCatalog`
- `duration`
- `shotCount`
- `subtitlesEnabled`

`topic`、`style`、`voice` 继续保留在 `JobForm` 组件内管理，但在提交时要与基础参数一起组合成统一 payload。

## API 与数据模型设计

### 创建任务请求

前端提交 `POST /api/jobs` 时，新增字段：

- `duration`
- `shotCount`
- `subtitlesEnabled`

保留现有字段：

- `topic`
- `style`
- `voice`

请求结构示例：

```json
{
  "topic": "职场新人如何快速成长",
  "style": "治愈干货",
  "voice": "auto",
  "duration": 30,
  "shotCount": 5,
  "subtitlesEnabled": true
}
```

### 后端请求模型

`CreateJobRequest` 扩展为接收：

- `duration: Literal[15, 30, 60]`
- `shot_count: Literal[3, 5, 7]` 或与前端字段统一命名
- `subtitles_enabled: bool`

命名建议优先保持现有接口风格一致；如果当前后端使用 Python 风格命名，需在序列化层明确与前端字段的映射规则，避免混乱。

### 任务数据持久层

`JobService` 中的任务对象应保存：

- `voice`
- `duration`
- `shotCount`
- `subtitlesEnabled`
- 固定 `aspectRatio = "9:16"`

这样任务详情页后续可以稳定展示“本次生成参数”。

## 工作流接入设计

### WorkflowState 扩展

LangGraph 状态新增：

- `duration`
- `shotCount`
- `subtitlesEnabled`
- `aspectRatio`

其中：
- `aspectRatio` 首版固定写入 `"9:16"`
- `voice` 继续沿用当前已存在的音色选择逻辑

### 节点使用规则

- `Director`：根据 `duration` 控制节奏目标
- `Script`：根据 `duration` 调整文案密度和篇幅
- `Storyboard`：根据 `shotCount` 控制镜头拆分数量
- `Voice`：继续读取音色选择结果
- `Editor`：读取 `subtitlesEnabled` 决定是否输出字幕叠加逻辑

即使当前渲染器对字幕开关仍是基础能力，也应先把这个字段真实穿透到节点和渲染输入，避免界面参数成为摆设。

## 任务详情页扩展

任务详情页本次补充展示：

- 主题
- 风格
- 音色选择结果
- 时长
- 分镜数量
- 字幕开关
- 画幅 `9:16`

这样首页和详情页之间形成一致的信息闭环。

## 错误处理

首页需要明确处理以下情况：

- 音色目录加载失败：使用本地兜底音色列表，不阻塞页面
- 创建任务失败：在左栏主操作区显示错误信息
- 后端不支持新增字段：通过测试先行避免接口漂移

后端需要明确处理：

- 非法时长值
- 非法分镜数量
- 缺失布尔字段时的默认行为

建议首版默认值：

- `duration = 30`
- `shotCount = 5`
- `subtitlesEnabled = true`
- `voice = "auto"`

## 测试方案

本次改造采用 TDD，至少覆盖以下测试：

### 前端组件测试

- `JobForm` 提交时能带上 `voice`
- `GenerationControls` 正确渲染 `15/30/60`
- `GenerationControls` 正确渲染 `3/5/7`
- `GenerationControls` 正确处理字幕开关
- 首页提交时 payload 包含新增字段

### 前端页面测试

- 首页能渲染三栏工作台关键文案
- 首页能显示当前音色目录来源
- 音色目录请求失败时仍能正常显示表单

### 后端 API 测试

- `POST /api/jobs` 接收新增字段
- 返回的任务详情保留新增字段
- 非法枚举值会被拒绝

### 工作流测试

- `WorkflowState` 含新增字段
- `shotCount` 能进入 `Storyboard` 节点
- `subtitlesEnabled` 能进入 `Editor` 节点

### 回归验证

- `python -m pytest backend/tests -q`
- `python -m ruff check backend`
- `python -m mypy app`
- `frontend` 下 `npm test`
- `frontend` 下 `npm run build`

## 实施顺序建议

1. 先补后端测试与请求模型
2. 再打通 `JobService` 和 `WorkflowState`
3. 然后补前端类型和提交 payload
4. 最后改首页布局、组件和任务详情展示

这样可以保证视觉改造不是孤立的外壳，而是建立在真实参数链路已经贯通的基础上。
