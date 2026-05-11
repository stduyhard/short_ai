from app.core.config import Settings
from app.observability.langsmith import maybe_traceable
from app.render.renderer import RenderRequest, Renderer
from app.workflows.state import WorkflowState


def build_editor_node(renderer: Renderer, current_settings: Settings | None = None):
    effective_settings = current_settings or Settings()

    @maybe_traceable(effective_settings, name="editor", run_type="chain")
    def run_editor(state: WorkflowState) -> WorkflowState:
        result = renderer.render(
            RenderRequest(
                job_id=state["job_id"],
                topic=state["topic"],
                script=state["script"],
                storyboard=state["storyboard"],
                visual_assets=state["visual_assets"],
                video_segments=state["video_segments"],
                voice_asset=state["voice_asset"],
                subtitles_enabled=state["subtitles_enabled"],
                aspect_ratio=state["aspect_ratio"],
            )
        )
        return {
            **state,
            "stages": [*state["stages"], "editor"],
            "final_video": result.video_path,
            "final_status": result.status,
        }

    return run_editor
