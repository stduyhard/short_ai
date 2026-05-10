from app.core.config import Settings
from app.workflows.graph import build_graph


def test_langgraph_workflow_runs_all_six_stages_in_order() -> None:
    graph = build_graph(Settings())

    result = graph.invoke(
        {
            "job_id": "graph-test",
            "topic": "高效晨间习惯",
            "style": "干货",
            "voice_selection": "auto",
            "duration": 30,
            "shot_count": 5,
            "subtitles_enabled": True,
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

    assert result["stages"] == [
        "director",
        "script",
        "storyboard",
        "visual",
        "voice",
        "editor",
    ]
    assert result["brief"]
    assert result["script"]
    assert result["storyboard"]
    assert result["visual_assets"]
    assert result["voice_asset"].endswith((".mp3", ".wav"))
    assert result["final_video"] == ""
    assert result["final_status"] == "degraded"


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
