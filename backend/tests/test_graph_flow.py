from app.workflows.graph import build_graph


def test_langgraph_workflow_runs_all_six_stages_in_order() -> None:
    graph = build_graph()

    result = graph.invoke(
        {
            "topic": "高效晨间习惯",
            "style": "干货",
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
    assert result["brief"] == "director completed"
    assert result["script"] == "script completed"
    assert result["storyboard"] == [{"shot": "1", "caption": "storyboard completed"}]
    assert result["visual_assets"] == ["visual completed"]
    assert result["voice_asset"] == "voice completed"
    assert result["final_video"] == "editor completed"
    assert result["final_status"] == "completed"
