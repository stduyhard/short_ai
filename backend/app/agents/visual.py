from app.providers.image import ImageProvider, ImageRequest
from app.workflows.state import WorkflowState


def build_visual_node(image_provider: ImageProvider):
    def run_visual(state: WorkflowState) -> WorkflowState:
        caption = state["storyboard"][0]["caption"]
        response = image_provider.generate(
            ImageRequest(
                prompt=f"为短视频分镜生成竖屏视觉素材：{caption}",
                metadata={"job_id": state["job_id"]},
            )
        )
        return {
            **state,
            "stages": [*state["stages"], "visual"],
            "visual_assets": [response.asset_uri],
        }

    return run_visual
