from app.workflows.graph import build_workflow


def test_langgraph_workflow_runs_all_six_stages_in_order() -> None:
    graph = build_workflow()

    result = graph.invoke(
        {
            "topic": "高效晨间习惯",
            "style": "干货",
            "completed_stages": [],
            "artifacts": {},
            "final_status": "pending",
        }
    )

    assert result["completed_stages"] == [
        "director",
        "script",
        "storyboard",
        "visual",
        "voice",
        "editor",
    ]
    assert result["artifacts"] == {
        "director": "director completed",
        "script": "script completed",
        "storyboard": "storyboard completed",
        "visual": "visual completed",
        "voice": "voice completed",
        "editor": "editor completed",
    }
    assert result["final_status"] == "completed"
