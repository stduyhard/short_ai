from langgraph.graph import END, START, StateGraph

from app.agents.director import build_director_node
from app.agents.editor import build_editor_node
from app.agents.script import build_script_node
from app.agents.storyboard import build_storyboard_node
from app.agents.visual import build_visual_node
from app.agents.voice import build_voice_node
from app.core.config import settings
from app.providers.factory import build_image_provider, build_llm_provider, build_tts_provider
from app.providers.storage import LocalStorageProvider
from app.render.renderer import Renderer
from app.workflows.state import WorkflowState


def build_graph():
    storage_provider = LocalStorageProvider(settings.artifacts_dir)
    llm_provider = build_llm_provider(settings)
    image_provider = build_image_provider(settings=settings, storage_provider=storage_provider)
    tts_provider = build_tts_provider(settings)
    renderer = Renderer(
        ffmpeg_binary=settings.ffmpeg_binary,
        work_dir=settings.artifacts_dir,
        allow_placeholder_when_unavailable=not _all_providers_are_real(settings),
    )

    graph_builder = StateGraph(WorkflowState)

    graph_builder.add_node("director", build_director_node(llm_provider))
    graph_builder.add_node("script", build_script_node(llm_provider))
    graph_builder.add_node("storyboard", build_storyboard_node(llm_provider))
    graph_builder.add_node("visual", build_visual_node(image_provider))
    graph_builder.add_node("voice", build_voice_node(tts_provider))
    graph_builder.add_node("editor", build_editor_node(renderer))

    graph_builder.add_edge(START, "director")
    graph_builder.add_edge("director", "script")
    graph_builder.add_edge("script", "storyboard")
    graph_builder.add_edge("storyboard", "visual")
    graph_builder.add_edge("visual", "voice")
    graph_builder.add_edge("voice", "editor")
    graph_builder.add_edge("editor", END)

    return graph_builder.compile()


def _all_providers_are_real(current_settings) -> bool:
    return (
        current_settings.llm_provider != "stub"
        and current_settings.image_provider != "stub"
        and current_settings.tts_provider != "stub"
    )
