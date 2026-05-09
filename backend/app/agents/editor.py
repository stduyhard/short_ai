from app.render.renderer import RenderRequest, Renderer
from app.workflows.state import WorkflowState


def build_editor_node(renderer: Renderer):
    def run_editor(state: WorkflowState) -> WorkflowState:
        result = renderer.render(
            RenderRequest(
                job_id=state["job_id"],
                topic=state["topic"],
                script=state["script"],
                storyboard=state["storyboard"],
                visual_assets=state["visual_assets"],
                voice_asset=state["voice_asset"],
            )
        )
        return {
            **state,
            "stages": [*state["stages"], "editor"],
            "final_video": result.video_path,
            "final_status": "completed",
        }

    return run_editor
