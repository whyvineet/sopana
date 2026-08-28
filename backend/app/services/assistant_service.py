from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.session_store import get_session_store
from app.integrations.llm.openrouter import get_chat_model

logger = logging.getLogger(__name__)

def _build_path_context(stored: dict[str, Any], context_step_id: str | None) -> str:
    learning_path = stored.get("learning_path") or {}
    steps = learning_path.get("steps") or []
    overall_progress = learning_path.get("overall_progress") or 0
    role_name = learning_path.get("role_name") or stored.get("target_role") or "your goal"

    context_parts: list[str] = []

    completed_count = sum(1 for s in steps if isinstance(s, dict) and s.get("completed"))
    context_parts.append(
        f"The learner is working toward: {role_name}\n"
        f"Overall progress: {int(round(float(overall_progress) * 100))}% "
        f"({completed_count}/{len(steps)} steps completed)"
    )

    current_step = next(
        (s for s in steps if isinstance(s, dict) and s.get("status") == "current"),
        None,
    )
    if current_step:
        context_parts.append(
            f"Current focus step: {current_step.get('title')}\n"
            f"Description: {current_step.get('description')}\n"
            f"Skills: {', '.join(current_step.get('skills') or [])}\n"
            f"Duration: {current_step.get('duration', 'Not specified')}"
        )
        if current_step.get("reason"):
            context_parts.append(f"Why this step is important: {current_step['reason']}")
        if current_step.get("prerequisites"):
            context_parts.append(f"Prerequisites for this step: {', '.join(current_step['prerequisites'])}")

    if context_step_id and steps:
        specific_step = next(
            (s for s in steps if isinstance(s, dict) and s.get("id") == context_step_id),
            None,
        )
        if specific_step and specific_step != current_step:
            context_parts.append(
                f"\nThe learner is asking about this specific step: {specific_step.get('title')}\n"
                f"Description: {specific_step.get('description')}\n"
                f"Why it's in the path: {specific_step.get('reason') or 'Part of the recommended learning sequence'}\n"
                f"Skills covered: {', '.join(specific_step.get('skills') or [])}\n"
                f"Prerequisites: {', '.join(specific_step.get('prerequisites') or []) or 'None'}\n"
                f"Expected outcome: {specific_step.get('expected_outcome') or 'Not specified'}"
            )
                                             
            resources = specific_step.get("resources") or []
            if resources:
                resource_lines = [
                    f"  • {r.get('title')} ({r.get('provider') or r.get('type', 'Resource')}) "
                    f"— {r.get('difficulty', '')} — {r.get('estimated_duration', '')}"
                    for r in resources[:3]
                    if isinstance(r, dict)
                ]
                if resource_lines:
                    context_parts.append("Recommended resources for this step:\n" + "\n".join(resource_lines))

    upcoming = [
        s.get("title")
        for s in steps
        if isinstance(s, dict) and s.get("status") == "upcoming" and s.get("title")
    ][:3]
    if upcoming:
        context_parts.append(f"Upcoming steps after current: {', '.join(upcoming)}")

    completed = [
        s.get("title")
        for s in steps
        if isinstance(s, dict) and s.get("completed") and s.get("title")
    ]
    if completed:
        context_parts.append(f"Already completed: {', '.join(completed)}")

    return "\n\n".join(context_parts) if context_parts else "No learning path context available."

def _build_learner_profile_context(stored: dict[str, Any]) -> str:
    parts: list[str] = []

    if stored.get("goal"):
        parts.append(f"Goal: {stored['goal']}")
    if stored.get("target_role"):
        parts.append(f"Target role: {stored['target_role']}")
    if stored.get("experience_level"):
        parts.append(f"Experience level: {stored['experience_level']}")

    skills = stored.get("skills") or []
    skill_names = [s.get("name") for s in skills if isinstance(s, dict) and s.get("name")]
    if skill_names:
        parts.append(f"Existing skills: {', '.join(skill_names)}")

    interests = stored.get("interests") or []
    if interests:
        parts.append(f"Learning interests: {', '.join(interests)}")

    objectives = stored.get("learning_objectives") or []
    if objectives:
        parts.append(f"Learning objectives: {', '.join(objectives)}")

    skill_gap = stored.get("skill_gap") or {}
    if skill_gap:
        strong = [item.get("skill_name") for item in skill_gap.get("strong", []) if isinstance(item, dict)]
        developing = [item.get("skill_name") for item in skill_gap.get("developing", []) if isinstance(item, dict)]
        missing = [item.get("skill_name") for item in skill_gap.get("missing", []) if isinstance(item, dict)]
        if strong:
            parts.append(f"Strong skills (can potentially skip): {', '.join(strong)}")
        if developing:
            parts.append(f"Skills in development: {', '.join(developing)}")
        if missing:
            parts.append(f"Skills to learn: {', '.join(missing)}")

    return "\n".join(parts) if parts else "Learner profile not yet complete."

_ASSISTANT_SYSTEM_PROMPT_TEMPLATE = """You are SOPĀNA, an expert AI learning advisor and companion.
You are helping a learner build and navigate their personalized learning path.

Your role is to:
- Answer questions about WHY specific skills or steps are in the learner's path
- Explain what skills involve and how to learn them
- Suggest whether steps can be skipped or reordered based on the learner's existing skills
- Provide encouragement and practical guidance when the learner struggles
- Recommend next actions based on the current path state
- Explain any learning resource or step in context

## Learner Profile:
{learner_profile}

## Current Learning Path Context:
{path_context}

## Guidelines:
- Always reference the learner's ACTUAL goal, skills, and path — do not make generic statements
- If asked "Why am I learning X?", connect it directly to their {target_role} goal
- If asked "Can I skip this?", check their existing skills — if they have the skill, acknowledge it
- If the learner is struggling, suggest foundational resources and be encouraging
- Keep responses concise but substantive (2-4 paragraphs maximum)
- Use markdown formatting for clarity when helpful
- Be warm, encouraging, and human — this is a learning journey, not a test
"""

def handle_chat(session_id: str, message: str, context_step_id: str | None = None) -> str:
    store = get_session_store()
    stored = store.get(session_id)
    if not stored:
        raise ValueError("Session not found")

    learner_profile = _build_learner_profile_context(stored)
    path_context = _build_path_context(stored, context_step_id)
    target_role = stored.get("target_role") or "your target role"

    system_prompt = _ASSISTANT_SYSTEM_PROMPT_TEMPLATE.format(
        learner_profile=learner_profile,
        path_context=path_context,
        target_role=target_role,
    )

    try:
        llm = get_chat_model()
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=message),
        ])
        return str(response.content)
    except Exception as exc:
        logger.error("Chat failed: %s", exc)
        return "I'm having trouble connecting to my brain right now. Please try again later."
