from typing import TypedDict


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
    video_segments: list[str]
    segment_duration_seconds: float
    voice_asset: str
    final_video: str
    final_status: str
