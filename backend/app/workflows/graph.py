from langgraph.graph import END, START, StateGraph

from app.agents.director import run_director
from app.agents.editor import run_editor
from app.agents.script import run_script
from app.agents.storyboard import run_storyboard
from app.agents.visual import run_visual
from app.agents.voice import run_voice
from app.workflows.state import WorkflowState


def build_graph():
    graph_builder = StateGraph(WorkflowState)

    graph_builder.add_node("director", run_director)
    graph_builder.add_node("script", run_script)
    graph_builder.add_node("storyboard", run_storyboard)
    graph_builder.add_node("visual", run_visual)
    graph_builder.add_node("voice", run_voice)
    graph_builder.add_node("editor", run_editor)

    graph_builder.add_edge(START, "director")
    graph_builder.add_edge("director", "script")
    graph_builder.add_edge("script", "storyboard")
    graph_builder.add_edge("storyboard", "visual")
    graph_builder.add_edge("visual", "voice")
    graph_builder.add_edge("voice", "editor")
    graph_builder.add_edge("editor", END)

    return graph_builder.compile()
