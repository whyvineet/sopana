from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage

from app.graph.extract import extract_learner_details
from app.graph.state import LearningState, StageName
from app.integrations.llm.openrouter import LLMConfigurationError
from app.services.option_service import (
    OptionItem,
    experience_options,
    objective_options,
    to_api_options,
)

logger = logging.getLogger(__name__)

STAGE_ORDER: list[StageName] = [
    "goal",
    "experience",
    "skill_discovery",
    "learning_interests",
    "objectives",
]

EXPERIENCE_ALIASES = {
    "none": "none",
    "no_hands_on_experience": "none",
    "casual": "casual",
    "coursework": "casual",
    "tutorials": "casual",
    "beginner_projects": "project",
    "beginner__projects": "project",
    "workshop": "workshop",
    "workshops": "workshop",
    "project": "project",
    "projects": "project",
    "academic_projects": "project",
    "academic__projects": "project",
    "built_a_few_projects": "project",
    "professional": "professional",
    "professional_experience": "professional",
    "professional__experience": "professional",
}


def _last_user_text(state: LearningState) -> str:
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage) and isinstance(msg.content, str):
            return msg.content.strip()
    return ""


def _missing(state: LearningState) -> list[str]:
    missing: list[str] = []
    if not state.get("target_role"):
        missing.append("role")
    if not state.get("experience_level"):
        missing.append("experience")
    if not state.get("selected_skill_ids") and state.get("experience_level") != "none":
        missing.append("skills")
    if not state.get("specific_interest"):
        missing.append("interests")
    if not state.get("learning_objectives"):
        missing.append("objectives")
    return missing


def _progress(stage: StageName) -> tuple[int, int]:
    index = STAGE_ORDER.index(stage) if stage in STAGE_ORDER else len(STAGE_ORDER) - 1
    return index + 1, len(STAGE_ORDER)


def _normalize_experience(value: str) -> str | None:
    key = value.strip().lower().replace("-", "_").replace(" ", "_").replace("/", "_")
    key = "_".join(part for part in key.split("_") if part)
    if key in EXPERIENCE_ALIASES:
        return EXPERIENCE_ALIASES[key]
    for alias, mapped in EXPERIENCE_ALIASES.items():
        if alias in key:
            return mapped
    return None


def _match_options(text: str, options: list[OptionItem]) -> list[OptionItem]:
    if not text:
        return []
    parts = [part.strip().lower() for part in text.replace(" and ", ",").split(",") if part.strip()]
    blob = text.lower()
    matched: list[OptionItem] = []
    for option in options:
        label = option.label.lower()
        option_id = option.id.lower()
        if any(part == label or part == option_id or part in label for part in parts):
            matched.append(option)
            continue
        if label in blob or option_id in blob:
            matched.append(option)
    return matched


def _upsert_skill(skills: list[dict[str, Any]], skill_name: str, level: str | None, source: str) -> None:
    skill_id = f"dynamic.{skill_name.lower().replace(' ', '_')}"
    for index, item in enumerate(skills):
        if item.get("skill_id") == skill_id or item.get("name") == skill_name:
            next_level = level or item.get("level") or "beginner"
            skills[index] = {
                "skill_id": skill_id,
                "name": skill_name,
                "level": next_level,
                "source": source,
            }
            return
    skills.append(
        {
            "skill_id": skill_id,
            "name": skill_name,
            "level": level or "beginner",
            "source": source,
        }
    )


def _apply_extraction(state: LearningState, text: str) -> dict[str, Any]:
    parsed = extract_learner_details(text)
    updates: dict[str, Any] = {}

    if parsed.goal_summary:
        updates["goal"] = parsed.goal_summary
        updates["goal_summary"] = parsed.goal_summary
    elif text and not state.get("goal"):
        updates["goal"] = text
        updates["goal_summary"] = text

    if parsed.target_role and not state.get("target_role"):
        updates["target_role"] = parsed.target_role

    if parsed.experience_level and not state.get("experience_level"):
        updates["experience_level"] = parsed.experience_level

    skill_payload = list(state.get("skills", []))
    for mention in parsed.skills:
        _upsert_skill(skill_payload, mention.skill_name, mention.level, "nlp_inference")
        
    if skill_payload:
        updates["skills"] = skill_payload
        updates["selected_skill_ids"] = [item["skill_id"] for item in skill_payload]

    interests = list(state.get("interests", []))
    if parsed.interests:
        interests = list(dict.fromkeys([*interests, *parsed.interests]))
        updates["interests"] = interests
        updates["specific_interest"] = True

    if parsed.learning_objectives:
        updates["learning_objectives"] = list(
            dict.fromkeys([*state.get("learning_objectives", []), *parsed.learning_objectives])
        )

    return updates


def _apply_option_text(state: LearningState, text: str) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    stage = state.get("current_stage", "goal")

    if stage == "experience":
        matched = _match_options(text, experience_options())
        if matched:
            updates["experience_level"] = _normalize_experience(matched[0].label) or _normalize_experience(
                matched[0].id.split("experience.", 1)[-1]
            )
        elif _normalize_experience(text):
            updates["experience_level"] = _normalize_experience(text)

    if stage == "skill_discovery":
        skill_payload = list(state.get("skills", []))
        if text.lower() in {"none", "none yet", "no", "nope"}:
            updates["selected_skill_ids"] = ["skill.none_yet"]
            updates["skills"] = skill_payload
        elif text:
            parts = [p.strip() for p in text.split(",")]
            for part in parts:
                if part:
                    _upsert_skill(skill_payload, part, None, "selection")
            updates["skills"] = skill_payload
            updates["selected_skill_ids"] = [item["skill_id"] for item in skill_payload]

    if stage == "learning_interests" and text:
        if text.lower() not in {"none", "no", "nope"}:
            interests = list(dict.fromkeys([*state.get("interests", []), text]))
            updates["interests"] = interests
        updates["specific_interest"] = True

    if stage == "objectives" and text:
        matched = _match_options(text, objective_options())
        labels = [option.label for option in matched] or [text]
        updates["learning_objectives"] = list(dict.fromkeys([*state.get("learning_objectives", []), *labels]))

    return updates


def _merged(state: LearningState, *patches: dict[str, Any]) -> LearningState:
    merged: dict[str, Any] = dict(state)
    for patch in patches:
        merged.update(patch)
    return merged


def _profile_summary(state: LearningState) -> str:
    skills = state.get("skills") or []
    skill_lines = ", ".join(
        f"{item.get('name')} — {(item.get('level') or 'beginner').title()}" for item in skills if item.get("name")
    ) or "None yet"
    interests = state.get("interests") or []
    objectives = state.get("learning_objectives") or []
    return (
        "Thanks. I have enough information to build your profile.\n\n"
        f"Goal: {state.get('goal_summary') or state.get('goal') or 'Not specified'}\n"
        f"Target Role: {state.get('target_role') or 'Not specified'}\n"
        f"Experience: {state.get('experience_level') or 'Not specified'}\n"
        f"Skills: {skill_lines}\n"
        f"Interest: {', '.join(interests) if interests else 'Not specified'}\n"
        f"Objective: {', '.join(objectives) if objectives else 'Not specified'}\n\n"
        "Now I'll build your personalized learning path."
    )


def _prompt(state: LearningState) -> dict[str, Any]:
    missing = _missing(state)

    if "role" in missing:
        current, total = _progress("goal")
        return {
            "current_stage": "goal",
            "last_reply": "What do you want to learn or become? (e.g. 'I want to become an AI engineer in healthcare')",
            "input_type": "text",
            "allow_custom_input": True,
            "options": [],
            "progress_current": current,
            "progress_total": total,
            "missing_information": missing,
            "error": None,
        }

    if "experience" in missing:
        current, total = _progress("experience")
        return {
            "current_stage": "experience",
            "last_reply": "What experience do you have?",
            "input_type": "single_select",
            "allow_custom_input": True,
            "options": to_api_options(experience_options()),
            "progress_current": current,
            "progress_total": total,
            "missing_information": missing,
            "error": None,
        }

    if "skills" in missing:
        current, total = _progress("skill_discovery")
        return {
            "current_stage": "skill_discovery",
            "last_reply": "What relevant skills do you already have? (Enter comma separated)",
            "input_type": "text",
            "allow_custom_input": True,
            "options": [{"id": "skill.none_yet", "label": "None yet"}],
            "progress_current": current,
            "progress_total": total,
            "missing_information": missing,
            "error": None,
        }

    if "interests" in missing:
        current, total = _progress("learning_interests")
        return {
            "current_stage": "learning_interests",
            "last_reply": "Any specific learning interests? (e.g. prefer videos, project-based)",
            "input_type": "text",
            "allow_custom_input": True,
            "options": [],
            "progress_current": current,
            "progress_total": total,
            "missing_information": missing,
            "error": None,
        }

    if "objectives" in missing:
        current, total = _progress("objectives")
        return {
            "current_stage": "objectives",
            "last_reply": "What is your main objective?",
            "input_type": "single_select",
            "allow_custom_input": True,
            "options": to_api_options(objective_options()),
            "progress_current": current,
            "progress_total": total,
            "missing_information": missing,
            "error": None,
        }

    current, total = _progress("objectives")
    
    if state.get("research_status") == "idle":
        return {
            "current_stage": "profile_review",
            "profile_complete": True,
            "last_reply": _profile_summary(state) + "\n\nResearching skills and resources for you... This may take a minute.",
            "input_type": "complete",
            "allow_custom_input": False,
            "options": [],
            "progress_current": current,
            "progress_total": total,
            "missing_information": [],
            "error": None,
        }
        
    return {
        "current_stage": "complete",
        "profile_complete": True,
        "last_reply": "Your personalized learning path is ready.",
        "input_type": "complete",
        "allow_custom_input": False,
        "options": [],
        "progress_current": current,
        "progress_total": total,
        "missing_information": [],
        "error": None,
    }


def conversation_node(state: LearningState) -> dict[str, Any]:
    if state.get("profile_complete") or state.get("current_stage") in {"profile_review", "complete"}:
        if not state.get("profile_complete"):
            return {**_prompt(state), "profile_complete": True}
        return {"profile_complete": True}

    text = _last_user_text(state)
    if not text:
        current, total = _progress("goal")
        return {
            "current_stage": "goal",
            "last_reply": "What do you want to learn or become?",
            "input_type": "text",
            "allow_custom_input": True,
            "options": [],
            "progress_current": current,
            "progress_total": total,
            "missing_information": _missing(state),
            "error": None,
        }

    try:
        option_updates = _apply_option_text(state, text)
        after_options = _merged(state, option_updates)
        needs_llm = not option_updates or (
            after_options.get("current_stage") == "goal" and not after_options.get("target_role")
        )
        
        options = state.get("options") or []
        labels = {str(opt.get("label", "")).lower() for opt in options if isinstance(opt, dict)}
        exact_option = text.lower() in labels or text.lower() in {
            str(opt.get("id", "")).lower() for opt in options if isinstance(opt, dict)
        }
        extraction_updates: dict[str, Any] = {}
        if not exact_option or needs_llm:
            extraction_updates = _apply_extraction(after_options, text)
        
        if after_options.get("current_stage") == "goal" and not extraction_updates.get("target_role") and not after_options.get("target_role"):
            extraction_updates["target_role"] = text.strip()
            
        merged = _merged(after_options, extraction_updates)
        prompt = _prompt(merged)
        result = {key: value for key, value in merged.items() if key != "messages"}
        result.update(prompt)
        return result
    except LLMConfigurationError as exc:
        return {
            "error": str(exc),
            "last_reply": "SOPĀNA is not connected to a model right now. Add OPENROUTER_API_KEY in backend/.env and retry.",
            "input_type": "text",
            "allow_custom_input": True,
            "options": [],
        }
    except Exception as exc:
        logger.exception("Conversation node failed")
        return {
            "error": f"Could not process that response: {exc}",
            "last_reply": "I hit an issue while processing that response. Please try once more.",
            "input_type": "text",
            "allow_custom_input": True,
        }
