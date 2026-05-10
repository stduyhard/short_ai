from app.providers.llm import LLMProvider, LLMRequest
from app.workflows.state import WorkflowState


def build_storyboard_node(llm_provider: LLMProvider):
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
            "storyboard": [
                {"shot": str(index + 1), "caption": f"{response.content} #{index + 1}"}
                for index in range(state["shot_count"])
            ],
        }

    return run_storyboard
