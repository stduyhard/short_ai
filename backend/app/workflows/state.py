from typing import TypedDict


class WorkflowState(TypedDict):
    topic: str
    style: str
    stages: list[str]
    brief: str
    script: str
    storyboard: str
    visual_assets: str
    voice_asset: str
    final_video: str
    final_status: str
