from app.providers.tts import TTSProvider, TTSRequest
from app.workflows.state import WorkflowState


def build_voice_node(tts_provider: TTSProvider):
    def run_voice(state: WorkflowState) -> WorkflowState:
        response = tts_provider.synthesize(
            TTSRequest(
                text=state["script"],
                metadata={"job_id": state["job_id"]},
            )
        )
        return {
            **state,
            "stages": [*state["stages"], "voice"],
            "voice_asset": response.asset_uri,
        }

    return run_voice
