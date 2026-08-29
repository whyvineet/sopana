from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, StateGraph

from app.graph.nodes import conversation_node
from app.graph.research_nodes import (
    compute_gap_node,
    extract_skills_node,
    finalize_path_node,
    generate_candidate_path_node,
    research_resources_node,
    research_resources_node,
    research_goal_node,
    validate_path_node,
)
from app.graph.state import LearningState


def _after_conversation(state: LearningState) -> str:
    if state.get("error"):
        return END
    if state.get("profile_complete") and state.get("research_status", "idle") == "idle":
        return "research_goal"
    return END


def _entry(state: LearningState) -> str:
    if state.get("error") or state.get("learning_path"):
        return "conversation"
        
    if state.get("profile_complete") and state.get("research_status", "idle") == "idle":
        return "research_goal"
        
    return "conversation"


@lru_cache
def get_graph():
    graph = StateGraph(LearningState)
    graph.add_node("conversation", conversation_node)
    graph.add_node("research_goal", research_goal_node)
    graph.add_node("extract_skills", extract_skills_node)
    graph.add_node("compute_gap", compute_gap_node)
    graph.add_node("candidate_path", generate_candidate_path_node)
    graph.add_node("validate_path", validate_path_node)
    graph.add_node("research_resources", research_resources_node)
    graph.add_node("finalize_path", finalize_path_node)
    graph.add_conditional_edges(
        "conversation", 
        _after_conversation, 
        {"research_goal": "research_goal", END: END}
    )
    graph.add_edge("research_goal", "extract_skills")
    graph.add_edge("extract_skills", "compute_gap")
    graph.add_edge("compute_gap", "candidate_path")
    graph.add_edge("candidate_path", "validate_path")
    
    def _after_validation(state: LearningState) -> str:
        if state.get("error"):
            return "candidate_path"
        return "research_resources"
        
    graph.add_conditional_edges(
        "validate_path",
        _after_validation,
        {"candidate_path": "candidate_path", "research_resources": "research_resources"}
    )
    
    graph.add_edge("research_resources", "finalize_path")
    graph.add_edge("finalize_path", END)
    graph.set_conditional_entry_point(
        _entry,
        {"conversation": "conversation", "research_goal": "research_goal"},
    )
    return graph.compile()
