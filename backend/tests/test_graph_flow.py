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
