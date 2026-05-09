from app.workflows.state import WorkflowState


def run_storyboard(state: WorkflowState) -> WorkflowState:
    return {
        **state,
        "stages": [*state["stages"], "storyboard"],
        "storyboard": [{"shot": "1", "caption": "storyboard completed"}],
    }
