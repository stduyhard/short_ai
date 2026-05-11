from dataclasses import dataclass

from app.agents.visual import build_visual_node
from app.workflows.state import WorkflowState


@dataclass
class _CapturedImageRequest:
    prompt: str


@dataclass
class _CapturedVideoRequest:
    prompt: str


class RecordingImageProvider:
    provider_name = "recording-image"

    def __init__(self) -> None:
        self.requests: list[_CapturedImageRequest] = []

    def generate(self, request):  # type: ignore[no-untyped-def]
        self.requests.append(_CapturedImageRequest(prompt=request.prompt))
        shot_number = len(self.requests)
        return type("ImageResponse", (), {"asset_uri": f"image-{shot_number}.png"})()


class RecordingVideoProvider:
    provider_name = "recording-video"

    def __init__(self) -> None:
        self.requests: list[_CapturedVideoRequest] = []

    def generate_segment(self, request):  # type: ignore[no-untyped-def]
        self.requests.append(_CapturedVideoRequest(prompt=request.prompt))
        shot_number = len(self.requests)
        return type("VideoSegmentResponse", (), {"asset_uri": f"segment-{shot_number}.mp4"})()


def test_visual_node_adds_continuity_and_shot_count_constraints_to_prompts() -> None:
    image_provider = RecordingImageProvider()
    video_provider = RecordingVideoProvider()
    visual_node = build_visual_node(image_provider, video_provider)

    state: WorkflowState = {
        "job_id": "job-1",
        "topic": "龟兔赛跑",
        "style": "童话绘本，温暖励志",
        "voice_selection": "auto",
        "duration": 15,
        "shot_count": 3,
        "subtitles_enabled": True,
        "aspect_ratio": "9:16",
        "stages": ["director", "script", "storyboard"],
        "brief": "保持童话绘本感",
        "script": "兔子骄傲，乌龟坚持，最终乌龟获胜。",
        "storyboard": [
            {"shot": "1", "caption": "兔子和乌龟站在起点", "visual": "森林赛道起点，兔子昂着头，乌龟沉稳看前方"},
            {"shot": "2", "caption": "兔子冲出去后回头嘲笑", "visual": "兔子领先回头笑，乌龟仍慢慢前进"},
            {"shot": "3", "caption": "乌龟坚持抵达终点", "visual": "终点线前，乌龟咬牙前进，兔子在后方惊讶"},
        ],
        "visual_assets": [],
        "video_segments": [],
        "segment_duration_seconds": 0.0,
        "voice_asset": "",
        "final_video": "",
        "final_status": "running",
    }

    visual_node(state)

    assert len(image_provider.requests) == 3
    assert len(video_provider.requests) == 3

    first_image_prompt = image_provider.requests[0].prompt
    second_image_prompt = image_provider.requests[1].prompt
    second_video_prompt = video_provider.requests[1].prompt

    assert "当前镜头：第1镜，共3镜" in first_image_prompt
    assert "当前镜头：第2镜，共3镜" in second_image_prompt
    assert "整条短片共有3个连续镜头" in first_image_prompt
    assert "承接上一镜" in second_image_prompt
    assert "上一镜文案：兔子和乌龟站在起点" in second_image_prompt
    assert "保持主角外观、服装、配色、场景氛围一致" in second_image_prompt
    assert "当前片段：第2镜，共3镜" in second_video_prompt
    assert "像同一故事中的相邻镜头" in second_video_prompt
    assert "不要做成彼此独立的3段短片" in second_video_prompt
