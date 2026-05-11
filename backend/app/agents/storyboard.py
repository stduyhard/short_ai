from app.core.config import Settings
from app.observability.langsmith import maybe_traceable
from app.providers.llm import LLMProvider, LLMRequest
from app.services.storyboard_parser import build_storyboard_shots
from app.workflows.state import WorkflowState


def build_storyboard_node(llm_provider: LLMProvider, current_settings: Settings | None = None):
    effective_settings = current_settings or Settings()

    @maybe_traceable(effective_settings, name="storyboard", run_type="chain")
    def run_storyboard(state: WorkflowState) -> WorkflowState:
        response = llm_provider.generate(
            LLMRequest(
                prompt=(
                    f"把这段文案拆成 {state['shot_count']} 个简化分镜，并返回一句画面字幕："
                    f"{state['script']}"
                ),
                metadata={"purpose": "storyboard", "job_id": state["job_id"]},
            )
        )
        return {
            **state,
            "stages": [*state["stages"], "storyboard"],
            "storyboard": build_storyboard_shots(response.content, state["shot_count"]),
        }

    return run_storyboard
