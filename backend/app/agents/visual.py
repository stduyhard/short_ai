from app.workflows.state import WorkflowState


def run_visual(state: WorkflowState) -> WorkflowState:
    return {
        **state,
        "stages": [*state["stages"], "visual"],
        "visual_assets": ["visual completed"],
    }
