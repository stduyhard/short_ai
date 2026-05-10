from app.providers.llm import LLMProvider, LLMRequest
from app.workflows.state import WorkflowState


def build_script_node(llm_provider: LLMProvider):
    def run_script(state: WorkflowState) -> WorkflowState:
        response = llm_provider.generate(
            LLMRequest(
                prompt=(
                    f"根据这个创意 brief 生成约 {state['duration']} 秒的中文口播文案，"
                    f"保持{state['style']}风格：{state['brief']}"
                ),
                metadata={"purpose": "script", "job_id": state["job_id"]},
            )
        )
        return {
            **state,
            "stages": [*state["stages"], "script"],
            "script": response.content,
        }

    return run_script
