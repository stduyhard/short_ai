from app.core.config import Settings
from app.observability.langsmith import maybe_traceable
from app.providers.llm import LLMProvider, LLMRequest
from app.workflows.state import WorkflowState


def build_director_node(llm_provider: LLMProvider, current_settings: Settings | None = None):
    effective_settings = current_settings or Settings()

    @maybe_traceable(effective_settings, name="director", run_type="chain")
    def run_director(state: WorkflowState) -> WorkflowState:
        response = llm_provider.generate(
            LLMRequest(
                prompt=(
                    f"为主题“{state['topic']}”生成一个{state['style']}风格的短视频创意 brief，"
                    f"目标时长约 {state['duration']} 秒，画幅为 {state['aspect_ratio']}。"
                ),
                metadata={"purpose": "brief", "job_id": state["job_id"]},
            )
        )
        return {
            **state,
            "stages": [*state["stages"], "director"],
            "brief": response.content,
        }

    return run_director
