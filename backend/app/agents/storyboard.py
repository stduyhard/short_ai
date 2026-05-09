from app.providers.llm import LLMProvider, LLMRequest
from app.workflows.state import WorkflowState


def build_storyboard_node(llm_provider: LLMProvider):
    def run_storyboard(state: WorkflowState) -> WorkflowState:
        response = llm_provider.generate(
            LLMRequest(
                prompt=f"把这段文案拆成 1 个简化分镜，并返回一句画面字幕：{state['script']}",
                metadata={"purpose": "storyboard", "job_id": state["job_id"]},
            )
        )
        return {
            **state,
            "stages": [*state["stages"], "storyboard"],
            "storyboard": [{"shot": "1", "caption": response.content}],
        }

    return run_storyboard
