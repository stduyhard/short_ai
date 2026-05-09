from app.providers.llm import LLMProvider, LLMRequest
from app.workflows.state import WorkflowState


def build_director_node(llm_provider: LLMProvider):
    def run_director(state: WorkflowState) -> WorkflowState:
        response = llm_provider.generate(
            LLMRequest(
                prompt=f"为主题“{state['topic']}”生成一个{state['style']}风格的短视频创意 brief。",
                metadata={"purpose": "brief", "job_id": state["job_id"]},
            )
        )
        return {
            **state,
            "stages": [*state["stages"], "director"],
            "brief": response.content,
        }

    return run_director
