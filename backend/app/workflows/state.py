from typing import TypedDict


class WorkflowState(TypedDict):
    topic: str
    style: str
    completed_stages: list[str]
    artifacts: dict[str, str]
    final_status: str


def build_stage_update(state: WorkflowState, stage_name: str) -> WorkflowState:
    return {
        "topic": state["topic"],
        "style": state["style"],
        "completed_stages": [*state["completed_stages"], stage_name],
        "artifacts": {
            **state["artifacts"],
            stage_name: f"{stage_name} completed",
        },
        "final_status": "completed" if stage_name == "editor" else "running",
    }
