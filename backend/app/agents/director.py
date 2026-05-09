from app.workflows.state import WorkflowState


def run_director(state: WorkflowState) -> WorkflowState:
    return {
        **state,
        "stages": [*state["stages"], "director"],
        "brief": "director completed",
    }
