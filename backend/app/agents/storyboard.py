from app.workflows.state import WorkflowState, build_stage_update


def run_storyboard(state: WorkflowState) -> WorkflowState:
    return build_stage_update(state, "storyboard")
