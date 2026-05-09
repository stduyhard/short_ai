from app.workflows.state import WorkflowState


def run_editor(state: WorkflowState) -> WorkflowState:
    return {
        **state,
        "stages": [*state["stages"], "editor"],
        "final_video": "artifacts/final.mp4",
        "final_status": "completed",
    }
