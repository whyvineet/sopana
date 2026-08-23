from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, StateGraph

from app.graph.nodes import (
    conversation_node,
    generate_learning_path_node,
    skill_gap_node,
)
from app.graph.state import LearningState


def _after_conversation(state: LearningState) -> str:
    if state.get("error"):
        return END
    if state.get("profile_complete") or state.get("current_stage") == "profile_review":
        return "skill_gap"
    return END


def _entry(state: LearningState) -> str:
    if state.get("current_stage") == "complete" and state.get("learning_path"):
        return "conversation"
    if (state.get("profile_complete") or state.get("current_stage") == "profile_review") and not state.get("learning_path"):
        return "skill_gap"
    return "conversation"


@lru_cache
def get_graph():
    graph = StateGraph(LearningState)
    graph.add_node("conversation", conversation_node)
    graph.add_node("skill_gap", skill_gap_node)
    graph.add_node("learning_path", generate_learning_path_node)
    graph.add_conditional_edges("conversation", _after_conversation, {"skill_gap": "skill_gap", END: END})
    graph.add_edge("skill_gap", "learning_path")
    graph.add_edge("learning_path", END)
    graph.set_conditional_entry_point(
        _entry,
        {"conversation": "conversation", "skill_gap": "skill_gap"},
    )
    return graph.compile()
