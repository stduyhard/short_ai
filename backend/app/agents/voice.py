from app.services.voice_selection import resolve_voice_selection
from app.providers.tts import TTSProvider, TTSRequest
from app.workflows.state import WorkflowState


def build_voice_node(tts_provider: TTSProvider, *, default_voice: str):
    def run_voice(state: WorkflowState) -> WorkflowState:
        selected_voice = resolve_voice_selection(
            style=state["style"],
            voice_selection=state["voice_selection"],
            default_voice=default_voice,
        )
        response = tts_provider.synthesize(
            TTSRequest(
                text=state["script"],
                voice=selected_voice,
                metadata={"job_id": state["job_id"]},
            )
        )
        return {
            **state,
            "stages": [*state["stages"], "voice"],
            "voice_asset": response.asset_uri,
        }

    return run_voice
