from app.agents.script import build_script_node


class FakeLLMProvider:
    provider_name = "fake"

    def __init__(self, content: str) -> None:
        self._content = content

    def generate(self, request):  # noqa: ANN001
        class Response:
            def __init__(self, content: str) -> None:
                self.content = content

        return Response(self._content)


def test_script_node_normalizes_model_output_into_plain_voiceover() -> None:
    provider = FakeLLMProvider(
        """【15秒口播文案】

（0-3s）清晨的风，先落在叶子上。
*它轻轻醒来，像一束还没说话的光。*

（3-7s）镜头推进
*你看，世界正在慢慢发亮。*

---

说明：
- 这段文案适合温柔女声
如需我继续生成分镜，请告诉我。
"""
    )
    run_script = build_script_node(provider)

    result = run_script(
        {
            "job_id": "script-test",
            "topic": "晨光短片",
            "style": "治愈",
            "voice_selection": "auto",
            "duration": 15,
            "shot_count": 3,
            "subtitles_enabled": True,
            "aspect_ratio": "9:16",
            "stages": [],
            "brief": "brief",
            "script": "",
            "storyboard": [],
            "visual_assets": [],
            "video_segments": [],
            "segment_duration_seconds": 0.0,
            "voice_asset": "",
            "final_video": "",
            "final_status": "pending",
        }
    )

    assert result["script"] == "它轻轻醒来，像一束还没说话的光。\n你看，世界正在慢慢发亮。"
