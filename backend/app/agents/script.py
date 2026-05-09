from app.workflows.state import WorkflowState


def run_script(state: WorkflowState) -> WorkflowState:
    return {
        **state,
        "stages": [*state["stages"], "script"],
        "script": "script completed",
    }
