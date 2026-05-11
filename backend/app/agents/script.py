from app.core.config import Settings
from app.observability.langsmith import maybe_traceable
from app.providers.llm import LLMProvider, LLMRequest
from app.services.script_normalizer import normalize_script_output
from app.workflows.state import WorkflowState


def build_script_node(llm_provider: LLMProvider, current_settings: Settings | None = None):
    effective_settings = current_settings or Settings()

    @maybe_traceable(effective_settings, name="script", run_type="chain")
    def run_script(state: WorkflowState) -> WorkflowState:
        response = llm_provider.generate(
            LLMRequest(
                prompt=(
                    f"根据这个创意 brief 生成约 {state['duration']} 秒的中文口播文案，"
                    f"保持{state['style']}风格：{state['brief']}。"
                    "只返回纯口播正文，不要标题、不要时间轴、不要分点、不要说明、不要 markdown、不要额外解释。"
                ),
                metadata={"purpose": "script", "job_id": state["job_id"]},
            )
        )
        return {
            **state,
            "stages": [*state["stages"], "script"],
            "script": normalize_script_output(response.content),
        }

    return run_script
