from __future__ import annotations

import uuid
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from app.core.session_store import get_session_store
from app.graph.build import get_graph
from app.graph.state import LearningState, initial_state


class SessionNotFoundError(Exception):
    pass


def _serialize_messages(messages: list[BaseMessage]) -> list[dict[str, str]]:
    out = []
    for message in messages:
        role = "human" if isinstance(message, HumanMessage) else "ai"
        out.append({"role": role, "content": message.content})
    return out


def _deserialize_messages(raw: list[dict[str, str]]) -> list[BaseMessage]:
    out: list[BaseMessage] = []
    for message in raw:
        if message["role"] == "human":
            out.append(HumanMessage(content=message["content"]))
        else:
            out.append(AIMessage(content=message["content"]))
    return out


def _to_storage(state: LearningState) -> dict[str, Any]:
    data = dict(state)
    data["messages"] = _serialize_messages(state["messages"])
    return data


def _from_storage(raw: dict[str, Any]) -> LearningState:
    raw = dict(raw)
    raw["messages"] = _deserialize_messages(raw.get("messages", []))
    return LearningState(**raw)


def _public_snapshot(state: LearningState) -> dict[str, Any]:
    complete = state.get("current_stage") == "complete" and bool(state.get("learning_path"))
    return {
        "session_id": state["session_id"],
        "stage": state["current_stage"],
        "reply": state.get("last_reply", ""),
        "input_type": state.get("input_type", "text"),
        "options": state.get("options", []),
        "allow_custom_input": state.get("allow_custom_input", True),
        "progress": {
            "current": state.get("progress_current", 1),
            "total": state.get("progress_total", 1),
        },
        "missing_information": state.get("missing_information", []),
        "profile": {
            "goal": state.get("goal"),
            "goal_summary": state.get("goal_summary"),
            "target_role": state.get("target_role"),
            "selected_domains": state.get("selected_domains", []),
            "experience_level": state.get("experience_level"),
            "interests": state.get("interests", []),
            "skills": state.get("skills", []),
            "learning_objectives": state.get("learning_objectives", []),
        },
        "onboarding_complete": complete,
        "skill_gap": state.get("skill_gap"),
        "learning_path": state.get("learning_path"),
        "error": state.get("error"),
    }


def start_conversation() -> dict[str, Any]:
    session_id = str(uuid.uuid4())
    state = initial_state(session_id)
    result = get_graph().invoke(state)
    get_session_store().set(session_id, _to_storage(result))
    return _public_snapshot(result)


def send_message(session_id: str, text: str, selected_options: list[str] | None = None) -> dict[str, Any]:
    stored = get_session_store().get(session_id)
    if stored is None:
        raise SessionNotFoundError(session_id)
    state = _from_storage(stored)

    normalized_text = text.strip() if text else ""
    if selected_options:
        label_by_id = {
            opt.get("id"): opt.get("label")
            for opt in state.get("options", [])
            if isinstance(opt, dict)
        }
        selected_labels = [label_by_id.get(option_id, option_id) for option_id in selected_options]
        normalized_text = ", ".join(selected_labels)

    if not normalized_text:
        raise ValueError("Message cannot be empty.")

    state["messages"] = [*state["messages"], HumanMessage(content=normalized_text)]
    result = get_graph().invoke(state)
    get_session_store().set(session_id, _to_storage(result))
    return _public_snapshot(result)


def get_profile(session_id: str) -> dict[str, Any]:
    stored = get_session_store().get(session_id)
    if stored is None:
        raise SessionNotFoundError(session_id)
    state = _from_storage(stored)
    snapshot = _public_snapshot(state)
    return snapshot["profile"] | {
        "session_id": session_id,
        "stage": state["current_stage"],
        "onboarding_complete": snapshot["onboarding_complete"],
    }


def get_learning_path(session_id: str) -> dict[str, Any] | None:
    stored = get_session_store().get(session_id)
    if stored is None:
        raise SessionNotFoundError(session_id)
    return stored.get("learning_path")


def get_skill_gap(session_id: str) -> dict[str, Any] | None:
    stored = get_session_store().get(session_id)
    if stored is None:
        raise SessionNotFoundError(session_id)
    return stored.get("skill_gap")
