from app.workflows.state import WorkflowState, build_stage_update


def run_editor(state: WorkflowState) -> WorkflowState:
    return build_stage_update(state, "editor")
