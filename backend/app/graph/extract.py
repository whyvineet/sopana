from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from app.integrations.llm.openrouter import get_chat_model
from app.schemas.profile import LearnerExtraction
from app.prompts import render_template

logger = logging.getLogger(__name__)

_MAX_HISTORY_FOR_EXTRACTION = 20

def _format_messages(messages: list[BaseMessage]) -> str:
    recent = messages[-_MAX_HISTORY_FOR_EXTRACTION:]
    lines: list[str] = []
    for msg in recent:
        role = "User" if isinstance(msg, HumanMessage) else "Sopana"
        content = str(msg.content).strip()
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines) if lines else ""


def extract_learner_details(text: str) -> LearnerExtraction:
    llm = get_chat_model().with_structured_output(LearnerExtraction)
    prompt = (
        "Extract structured learner information from the message. "
        "Preserve full specificity — identify industry, function, and specialization separately. "
        "Compose target_role from function + specialization (e.g. 'Brand Marketing Strategist', not 'Marketing Professional'). "
        "Map 'nothing', 'nil', 'none', 'no experience' to experience_level='none'. "
        "Set role_confidence to 'low' when goal is broad and 'high' when function+specialization+career_intent are all known. "
        "NEVER set target_role to greetings, casual phrases, or non-career text."
    )
    return llm.invoke([SystemMessage(content=prompt), HumanMessage(content=text)])

def extract_from_history(
    messages: list[BaseMessage],
    current_profile: dict[str, Any],
) -> LearnerExtraction:
    llm = get_chat_model().with_structured_output(LearnerExtraction)

    history_str = _format_messages(messages)
    if not history_str:
        return LearnerExtraction()

    prompt_content = render_template(
        "extraction.jinja",
        history_str=history_str,
        profile=current_profile,
    )

    try:
        result: LearnerExtraction = llm.invoke([
            HumanMessage(content=prompt_content),
        ])
        logger.debug(
            "History extraction: role=%s industry=%s function=%s specialization=%s career=%s confidence=%s",
            result.target_role,
            result.industry,
            result.function,
            result.specialization,
            result.career_intent,
            result.role_confidence,
        )
        return result
    except Exception as exc:
        logger.error("History-aware extraction failed: %s", exc)
        last_human = next(
            (msg for msg in reversed(messages) if isinstance(msg, HumanMessage)),
            None,
        )
        if last_human:
            try:
                return extract_learner_details(str(last_human.content))
            except Exception as fallback_exc:
                logger.error("Fallback extraction also failed: %s", fallback_exc)
        return LearnerExtraction()

def build_learner_profile_json(state: dict[str, Any]) -> dict[str, Any]:
    skills = state.get("skills") or []
    skill_names = [s.get("name") for s in skills if isinstance(s, dict) and s.get("name")]

    return {
        "goal": state.get("goal") or state.get("goal_summary"),
        "target_role": state.get("target_role"),
        "industry": state.get("industry"),
        "function": state.get("function"),
        "specialization": state.get("specialization"),
        "career_intent": state.get("career_intent"),
        "experience": state.get("experience_level"),
        "skills": skill_names,
        "interests": state.get("interests") or [],
        "learning_objectives": state.get("learning_objectives") or [],
    }
