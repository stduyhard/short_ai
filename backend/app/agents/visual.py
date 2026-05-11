from app.core.config import Settings
from app.observability.langsmith import maybe_traceable
from app.providers.image import ImageProvider, ImageRequest
from app.providers.video import VideoProvider, VideoSegmentRequest
from app.workflows.state import WorkflowState


def build_visual_node(
    image_provider: ImageProvider,
    video_provider: VideoProvider,
    current_settings: Settings | None = None,
):
    effective_settings = current_settings or Settings()

    @maybe_traceable(effective_settings, name="visual", run_type="chain")
    def run_visual(state: WorkflowState) -> WorkflowState:
        visual_assets: list[str] = []
        video_segments: list[str] = []
        segment_duration_seconds = state["duration"] / state["shot_count"]
        total_shots = max(state["shot_count"], len(state["storyboard"]))
        previous_shot: dict[str, str] | None = None
        for shot in state["storyboard"]:
            visual_description = shot.get("visual") or shot["caption"]
            response = image_provider.generate(
                ImageRequest(
                    prompt=_build_image_prompt(
                        state=state,
                        shot=shot,
                        visual_description=visual_description,
                        total_shots=total_shots,
                        previous_shot=previous_shot,
                    ),
                    size="1024x1536",
                    metadata={"job_id": state["job_id"]},
                )
            )
            visual_assets.append(response.asset_uri)
            segment_response = video_provider.generate_segment(
                VideoSegmentRequest(
                    image_path=response.asset_uri,
                    prompt=_build_video_prompt(
                        state=state,
                        shot=shot,
                        visual_description=visual_description,
                        total_shots=total_shots,
                        previous_shot=previous_shot,
                    ),
                    duration_seconds=segment_duration_seconds,
                    metadata={"job_id": state["job_id"], "shot": shot["shot"]},
                )
            )
            video_segments.append(segment_response.asset_uri)
            previous_shot = shot

        return {
            **state,
            "stages": [*state["stages"], "visual"],
            "visual_assets": visual_assets,
            "video_segments": video_segments,
            "segment_duration_seconds": segment_duration_seconds,
        }

    return run_visual


def _build_image_prompt(
    *,
    state: WorkflowState,
    shot: dict[str, str],
    visual_description: str,
    total_shots: int,
    previous_shot: dict[str, str] | None,
) -> str:
    continuity_lines = [
        f"为中文短视频生成连续分镜竖屏画面，整条短片共有{total_shots}个连续镜头。",
        f"主题：{state['topic']}。",
        f"风格：{state['style']}。",
        f"当前镜头：第{shot['shot']}镜，共{total_shots}镜。",
        f"当前镜头文案：{shot['caption']}。",
        f"当前画面描述：{visual_description}。",
        "保持主角外观、服装、配色、场景氛围一致，延续同一绘本世界观。",
        "镜头只做自然推进，不要突然切换成完全不同的角色、场景、时间和画风。",
        "构图要像同一条故事短片里的连续镜头，不要做成彼此独立的宣传海报。",
        "不要出现海报排版、不要出现大段文字、不要出现水印。",
    ]

    if previous_shot is None:
        continuity_lines.append("这是开场镜头，请建立后续镜头会沿用的角色形象与场景基调。")
    else:
        previous_visual = previous_shot.get("visual") or previous_shot["caption"]
        continuity_lines.extend(
            [
                "承接上一镜，保持叙事连续。",
                f"上一镜文案：{previous_shot['caption']}。",
                f"上一镜画面：{previous_visual}。",
            ]
        )

    return "".join(continuity_lines)


def _build_video_prompt(
    *,
    state: WorkflowState,
    shot: dict[str, str],
    visual_description: str,
    total_shots: int,
    previous_shot: dict[str, str] | None,
) -> str:
    continuity_lines = [
        "基于这张分镜图生成竖屏短视频片段。",
        f"主题：{state['topic']}。",
        f"风格：{state['style']}。",
        f"当前片段：第{shot['shot']}镜，共{total_shots}镜。",
        f"当前镜头文案：{shot['caption']}。",
        f"当前画面描述：{visual_description}。",
        "像同一故事中的相邻镜头，保持角色长相、服装、配色和场景基调一致。",
        "主体做轻微自然运动，动作与情绪要延续前后镜头，不要闪烁、变脸、跳景。",
        f"不要做成彼此独立的{total_shots}段短片，也不要生成海报式静止画面或大段文字。",
    ]

    if previous_shot is None:
        continuity_lines.append("这是开场片段，动作应自然建立故事开场状态。")
    else:
        previous_visual = previous_shot.get("visual") or previous_shot["caption"]
        continuity_lines.extend(
            [
                "承接上一镜动作与情绪。",
                f"上一镜文案：{previous_shot['caption']}。",
                f"上一镜画面：{previous_visual}。",
            ]
        )

    return "".join(continuity_lines)
