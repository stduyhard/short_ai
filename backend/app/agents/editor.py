from app.workflows.state import WorkflowState


def run_editor(state: WorkflowState) -> WorkflowState:
    return {
        **state,
        "stages": [*state["stages"], "editor"],
        "final_video": "editor completed",
        "final_status": "completed",
    }
