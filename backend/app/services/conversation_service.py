from __future__ import annotations

import uuid
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from app.core.session_store import get_session_store
from app.graph.build import get_graph
from app.graph.state import LearningState, initial_state
from app.knowledge.repository import get_repository


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


def _build_dashboard(state: LearningState) -> dict[str, Any] | None:
    learning_path = state.get("learning_path") or {}
    if not learning_path:
        return None

    repo = get_repository()

    steps = learning_path.get("steps") or []
    current_focus_step_id = learning_path.get("current_focus_step_id")
    current_index = 0
    for index, step in enumerate(steps):
        if step.get("id") == current_focus_step_id:
            current_index = index
            break

    current_step = steps[current_index] if steps else None
    next_step = steps[current_index + 1] if current_index + 1 < len(steps) else None

    strong_skills = [
        item.get("skill_name")
        for item in (state.get("skill_gap") or {}).get("strong", [])
        if isinstance(item, dict) and item.get("skill_name")
    ]

    completed_step_skills: list[str] = []
    for step in steps:
        if not isinstance(step, dict) or not step.get("completed"):
            continue
        for skill_id in step.get("skills") or []:
            skill = repo.get_skill(skill_id)
            completed_step_skills.append(skill.name if skill else skill_id)

    if not strong_skills and not completed_step_skills:
        completed_step_skills = [
            item.get("name")
            for item in state.get("skills", [])
            if isinstance(item, dict) and item.get("name")
        ]

    developed_skills = list(dict.fromkeys([*strong_skills, *completed_step_skills]))

    upcoming_titles = [
        step.get("title")
        for step in steps[current_index + 1 :]
        if isinstance(step, dict) and step.get("title")
    ][:4]

    return {
        "target": state.get("target_role") or learning_path.get("role_name") or "Your role",
        "percent_complete": int(round(float(learning_path.get("overall_progress") or 0) * 100)),
        "current_focus": current_step.get("title") if isinstance(current_step, dict) else "Start your first step",
        "next_action": next_step.get("title") if isinstance(next_step, dict) else "Continue current focus",
        "skills_developed": developed_skills,
        "upcoming_steps": upcoming_titles,
    }


def _recompute_learning_path_progress(learning_path: dict[str, Any]) -> dict[str, Any]:
    steps = learning_path.get("steps") or []
    if not isinstance(steps, list):
        steps = []

    for step in steps:
        if not isinstance(step, dict):
            continue
        if step.get("completed") or step.get("status") in {"completed", "complete"}:
            step["completed"] = True
            step["status"] = "completed"
        else:
            step["completed"] = False

    incomplete_steps = [step for step in steps if isinstance(step, dict) and not step.get("completed")]
    current_focus_id = learning_path.get("current_focus_step_id")
    has_current_focus = any(step.get("id") == current_focus_id for step in incomplete_steps)
    if not has_current_focus:
        current_focus_id = incomplete_steps[0].get("id") if incomplete_steps else None

    for step in incomplete_steps:
        step["status"] = "current" if step.get("id") == current_focus_id else "upcoming"

    total = len([step for step in steps if isinstance(step, dict)])
    completed = len([step for step in steps if isinstance(step, dict) and step.get("completed")])

    learning_path["steps"] = steps
    learning_path["current_focus_step_id"] = current_focus_id
    learning_path["overall_progress"] = round((completed / total), 2) if total else 0.0
    return learning_path


def _learning_path_step_update_snapshot(state: LearningState) -> dict[str, Any]:
    return {
        "learning_path": state.get("learning_path"),
        "dashboard": _build_dashboard(state),
    }


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
        "dashboard": _build_dashboard(state),
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


def get_dashboard(session_id: str) -> dict[str, Any] | None:
    stored = get_session_store().get(session_id)
    if stored is None:
        raise SessionNotFoundError(session_id)
    state = _from_storage(stored)
    return _build_dashboard(state)


def start_learning_step(session_id: str, step_id: str) -> dict[str, Any]:
    stored = get_session_store().get(session_id)
    if stored is None:
        raise SessionNotFoundError(session_id)

    updated = dict(stored)
    learning_path = dict(updated.get("learning_path") or {})
    steps = learning_path.get("steps") or []
    if not steps:
        raise ValueError("Learning path not generated yet for this session.")

    target_step = next((step for step in steps if isinstance(step, dict) and step.get("id") == step_id), None)
    if target_step is None:
        raise ValueError("Unknown learning step.")

    for step in steps:
        if not isinstance(step, dict) or step.get("completed"):
            continue
        step["status"] = "current" if step.get("id") == step_id else "upcoming"

    target_step["completed"] = False
    target_step["status"] = "current"
    learning_path["steps"] = steps
    updated["learning_path"] = _recompute_learning_path_progress(learning_path)

    get_session_store().set(session_id, updated)
    state = _from_storage(updated)
    return _learning_path_step_update_snapshot(state)


def complete_learning_step(session_id: str, step_id: str) -> dict[str, Any]:
    stored = get_session_store().get(session_id)
    if stored is None:
        raise SessionNotFoundError(session_id)

    updated = dict(stored)
    learning_path = dict(updated.get("learning_path") or {})
    steps = learning_path.get("steps") or []
    if not steps:
        raise ValueError("Learning path not generated yet for this session.")

    target_step = next((step for step in steps if isinstance(step, dict) and step.get("id") == step_id), None)
    if target_step is None:
        raise ValueError("Unknown learning step.")

    target_step["completed"] = True
    target_step["status"] = "completed"

    learning_path["steps"] = steps
    updated["learning_path"] = _recompute_learning_path_progress(learning_path)

    get_session_store().set(session_id, updated)
    state = _from_storage(updated)
    return _learning_path_step_update_snapshot(state)
