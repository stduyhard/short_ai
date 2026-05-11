# 分镜图生视频设计

日期：2026-05-10  
项目：`short_video`

## 背景

当前系统已经能生成：

- 文案
- 分镜
- 分镜配图
- 配音
- 最终 `mp4`

但当前成片本质上仍是：

- 单图循环
- 或多图拼接的图片视频

这类结果虽然是一个可播放的 `mp4`，但并不具备用户所期待的“真正视频感”。用户已经明确指出，参考视频的关键特征是：

- 主体在动
- 镜头在连续变化
- 不是静态图片播放

因此，本轮目标不是继续优化“图片视频”，而是把成片链路升级为：

`每个分镜先生成图片，再生成对应视频片段，最后把多个视频片段拼接成完整视频。`

## 目标

首版实现以下能力：

- 只接入 `Qwen`
- 每个分镜生成 `1 张图`
- 每个分镜基于该图片生成 `1 段短视频`
- 每个分镜视频时长按总时长与分镜数自动平均分配
- 最终将多个短视频片段、配音、字幕合成为 `1 个完整 mp4`
- 首页继续在当前页展示生成进度、素材和最终成片

## 非目标

本轮不做：

- 多供应商视频模型抽象
- 前端逐镜头手动配置时长
- 数字人口播
- 嘴型驱动
- 背景音乐自动卡点
- 每镜头复杂转场配置
- 多版本并行成片

## 总体方案

当前数据流：

`topic/style -> brief -> script -> storyboard -> visual_assets -> voice -> render`

升级后数据流：

`topic/style -> brief -> script -> storyboard -> visual_assets -> video_segments -> voice -> render`

其中新增的关键产物是：

- `video_segments`

它表示每个分镜生成出来的短视频片段路径列表。  
最终 renderer 不再基于静态图片直接出片，而是基于 `video_segments` 合成最终视频。

## 时长策略

采用用户已确认的首版策略：

- `segment_duration_seconds = total_duration / shot_count`

例如：

- `30 秒 / 5 镜头 = 每镜头约 6 秒`
- `15 秒 / 3 镜头 = 每镜头约 5 秒`

首版统一按平均分配，不允许前端单独调整某一镜头时长。

## 工作流改动

### 1. WorkflowState 扩展

在工作流状态中新增：

- `video_segments: list[str]`
- `segment_duration_seconds: float`

要求：

- `segment_duration_seconds` 在任务启动时即可确定
- `video_segments` 由视觉视频化阶段产出

### 2. Storyboard 产物继续保留

分镜依然保留结构化输出：

- `shot`
- `caption`
- `visual`

其中：

- `caption` 用于字幕和前端展示
- `visual` 用于图片生成和视频片段生成提示

### 3. Visual 节点升级

`visual` 节点从“只出图”升级为“两段式素材节点”：

1. 为每个分镜生成图片
2. 基于该图片为每个分镜生成短视频片段

节点输出：

- `visual_assets`
- `video_segments`

这样设计的原因是：

- 图片素材仍有调试价值
- 前端仍可以展示分镜首帧
- 视频片段失败时，后续可以只重试视频化阶段

## Provider 设计

首版只接 `Qwen`，不做复杂多供应商抽象。

新增一个视频 provider，职责是：

- 输入：图片路径、分镜提示、目标时长
- 输出：单段 `mp4`

建议接口形态：

`generate_segment(image_path, prompt, duration_seconds, metadata) -> VideoSegmentResponse`

返回值至少包括：

- `asset_uri`
- `provider_name`

## Renderer 设计

renderer 改成基于视频片段而不是静态图片。

### 输入

新增依赖：

- `video_segments`

保留：

- `voice_asset`
- `storyboard`
- `subtitles_enabled`
- `aspect_ratio`

### 输出

最终仍输出：

- `final.mp4`

### 合成策略

首版策略：

1. 顺序拼接所有 `video_segments`
2. 混入 `voice_asset`
3. 根据 `subtitles_enabled` 决定是否叠字幕
4. 导出最终 `mp4`

### 降级策略

如果某个视频片段阶段失败：

- 整条任务标记为 `failed`
- `errorMessage` 明确说明失败位于视频片段生成阶段

不再退回“静态图片视频”作为静默替代结果，避免用户误以为已经达成“会动的视频”目标。

## 前端改动

首页保持“当前页生成”的交互，不跳转详情页。

### 首页当前任务区展示

保留：

- 阶段进度
- 图片区
- 音频区
- 最终视频区

新增或调整：

- 图片区展示每个分镜首帧图，而不是只展示 1 张
- 视频结果区明确展示最终成片
- 如果视频片段阶段失败，首页直接显示 `errorMessage`

### 交互状态

用户已确认：

- 点击开始生成后，首页表单进入 `生成中` 状态
- 生成期间禁用表单和参数区域
- 生成完成或失败后恢复可编辑

## 数据结构改动

后端：

- `WorkflowState` 新增 `video_segments`、`segment_duration_seconds`
- `JobDetailResponse` 建议新增：
  - `videoSegments?: list[str] | None`

前端：

- `JobDetail` 类型增加：
  - `videoSegments?: string[] | null`

## 错误处理

需要明确区分以下失败类型：

- 文案失败
- 分镜失败
- 图片生成失败
- 视频片段生成失败
- 渲染失败

首页和详情页都应显示：

- 当前任务状态
- `errorMessage`

不能只显示一个 `failed` 标签而没有原因。

## 测试方案

### 1. Provider 层测试

验证视频 provider 至少能返回合法 `mp4` 路径。

### 2. 工作流测试

验证：

- `segment_duration_seconds` 计算正确
- `video_segments` 数量与 `shot_count` 一致
- `visual_assets` 仍然保留

### 3. Renderer 测试

验证 renderer 使用的是：

- `video_segments`

而不是：

- `visual_assets`

### 4. 端到端烟雾测试

验证真实任务完成后同时存在：

- `visualAssets`
- `videoSegments`
- `finalVideo`

## 验收标准

当用户输入主题和风格后，系统应能：

1. 生成分镜
2. 为每个分镜生成图片
3. 为每个分镜生成短视频片段
4. 将多个视频片段合成为一个完整 `mp4`
5. 在首页当前任务区看到：
   - 进度
   - 图片
   - 音频
   - 最终视频

最终效果标准：

- 成片不再是“静态图片视频”
- 成片至少由多个真正的视频片段构成
- 用户可以明确感知镜头在动，而不是只有一张图在播
