from langgraph.graph import END, START, StateGraph

from app.agents.director import build_director_node
from app.agents.editor import build_editor_node
from app.agents.script import build_script_node
from app.agents.storyboard import build_storyboard_node
from app.agents.visual import build_visual_node
from app.agents.voice import build_voice_node
from app.core.config import settings
from app.providers.image import OpenAIImageProvider, StubImageProvider
from app.providers.llm import OpenAILLMProvider, StubLLMProvider
from app.providers.storage import LocalStorageProvider
from app.providers.tts import OpenAITTSProvider, StubTTSProvider
from app.render.renderer import Renderer
from app.workflows.state import WorkflowState


def build_graph():
    storage_provider = LocalStorageProvider(settings.artifacts_dir)
    llm_provider = (
        OpenAILLMProvider(api_key=settings.openai_api_key, model=settings.openai_text_model)
        if settings.openai_api_key
        else StubLLMProvider()
    )
    image_provider = (
        OpenAIImageProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_image_model,
            storage_provider=storage_provider,
        )
        if settings.openai_api_key
        else StubImageProvider(storage_provider)
    )
    tts_provider = (
        OpenAITTSProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_tts_model,
            default_voice=settings.openai_tts_voice,
            output_dir=settings.artifacts_dir,
        )
        if settings.openai_api_key
        else StubTTSProvider(settings.artifacts_dir)
    )
    renderer = Renderer(
        ffmpeg_binary=settings.ffmpeg_binary,
        work_dir=settings.artifacts_dir,
        allow_placeholder_when_unavailable=not bool(settings.openai_api_key),
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
