from app.workflows.state import WorkflowState, build_stage_update


def run_script(state: WorkflowState) -> WorkflowState:
    return build_stage_update(state, "script")
