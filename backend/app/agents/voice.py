from app.workflows.state import WorkflowState


def run_voice(state: WorkflowState) -> WorkflowState:
    return {
        **state,
        "stages": [*state["stages"], "voice"],
        "voice_asset": "voice completed",
    }
