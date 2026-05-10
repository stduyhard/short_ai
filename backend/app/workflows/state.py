from typing import TypedDict


class WorkflowState(TypedDict):
    job_id: str
    topic: str
    style: str
    voice_selection: str
    stages: list[str]
    brief: str
    script: str
    storyboard: list[dict[str, str]]
    visual_assets: list[str]
    voice_asset: str
    final_video: str
    final_status: str
