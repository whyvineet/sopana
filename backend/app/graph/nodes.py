from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage

from app.graph.extract import extract_learner_details, infer_role_family
from app.graph.state import LearningState, StageName
from app.integrations.llm.openrouter import LLMConfigurationError
from app.knowledge.repository import get_repository
from app.services.learning_path_service import generate_learning_path
from app.services.option_service import (
    OptionItem,
    domain_options,
    experience_options,
    objective_options,
    proficiency_options,
    role_options,
    skill_options,
    to_api_options,
)
from app.services.skill_gap_service import compute_skill_gap

logger = logging.getLogger(__name__)

STAGE_ORDER: list[StageName] = [
    "goal",
    "domain_discovery",
    "experience",
    "skill_discovery",
    "skill_proficiency",
    "learning_interests",
    "objectives",
]

LEVELS = ["none", "beginner", "basic", "intermediate", "advanced", "expert"]
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
    if not state.get("matched_role_id"):
        missing.append("role")
    if not state.get("selected_domain_ids"):
        missing.append("domains")
    if not state.get("experience_level"):
        missing.append("experience")
    if not state.get("selected_skill_ids") and state.get("experience_level") != "none":
        missing.append("skills")
    if state.get("pending_proficiency_skill_ids"):
        missing.append("proficiency")
    if not state.get("specific_interest"):
        missing.append("interests")
    if not state.get("learning_objectives"):
        missing.append("objectives")
    return missing


def _progress(stage: StageName) -> tuple[int, int]:
    index = STAGE_ORDER.index(stage) if stage in STAGE_ORDER else len(STAGE_ORDER) - 1
    return index + 1, len(STAGE_ORDER)


def _role(state: LearningState):
    return get_repository().get_role(state.get("matched_role_id"))


def _normalize_experience(value: str) -> str | None:
    key = value.strip().lower().replace("-", "_").replace(" ", "_").replace("/", "_")
    key = "_".join(part for part in key.split("_") if part)
    if key in EXPERIENCE_ALIASES:
        return EXPERIENCE_ALIASES[key]
    for alias, mapped in EXPERIENCE_ALIASES.items():
        if alias in key:
            return mapped
    return None


def _normalize_level(value: str | None) -> str | None:
    if not value:
        return None
    v = value.strip().lower()
    if v in LEVELS:
        return v
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


def _upsert_skill(skills: list[dict[str, Any]], skill_id: str, name: str, level: str | None, source: str) -> None:
    for index, item in enumerate(skills):
        if item.get("skill_id") == skill_id:
            next_level = level or item.get("level") or "beginner"
            skills[index] = {
                "skill_id": skill_id,
                "name": name,
                "level": next_level,
                "source": source,
            }
            return
    skills.append(
        {
            "skill_id": skill_id,
            "name": name,
            "level": level or "beginner",
            "source": source,
        }
    )


def _apply_extraction(state: LearningState, text: str) -> dict[str, Any]:
    repo = get_repository()
    parsed = extract_learner_details(text)
    updates: dict[str, Any] = {}


    if parsed.goal_summary:
        updates["goal"] = parsed.goal_summary
        updates["goal_summary"] = parsed.goal_summary
    elif text and not state.get("goal"):
        updates["goal"] = text
        updates["goal_summary"] = text

    role = repo.find_role_by_name(parsed.target_role or "")
    text_l = text.lower()
    specific_role_words = any(
        word in text_l for word in ("engineer", "scientist", "developer", "analyst", "actor", "acting")
    )
    if (
        role
        and parsed.role_confidence == "high"
        and specific_role_words
        and not state.get("matched_role_id")
    ):
        updates["target_role"] = role.name
        updates["matched_role_id"] = role.id

    if parsed.experience_level and not state.get("experience_level"):
        updates["experience_level"] = parsed.experience_level

    selected_domains = list(state.get("selected_domains", []))
    selected_domain_ids = list(state.get("selected_domain_ids", []))
    role_obj = repo.get_role(updates.get("matched_role_id") or state.get("matched_role_id"))
    if role_obj:
        for name in parsed.domains:
            for option in domain_options(role_obj):
                if (name.lower() in option.label.lower() or option.label.lower() in name.lower()) and (option.id not in selected_domain_ids):
                        selected_domain_ids.append(option.id)
                        selected_domains.append(option.label)
    if selected_domain_ids:
        updates["selected_domains"] = selected_domains
        updates["selected_domain_ids"] = selected_domain_ids
        updates["interests"] = list(dict.fromkeys([*state.get("interests", []), *selected_domains]))

    skill_payload = list(state.get("skills", []))
    pending = list(state.get("pending_proficiency_skill_ids", []))
    for mention in parsed.skills:
        skill = repo.find_skill_by_name(mention.skill_name)
        if not skill:
            continue
        level = _normalize_level(mention.level)
        _upsert_skill(skill_payload, skill.id, skill.name, level, "nlp_inference")
        if level is None and skill.id not in pending:
            pending.append(skill.id)
        if level and skill.id in pending:
            pending.remove(skill.id)
    if skill_payload:
        updates["skills"] = skill_payload
        updates["selected_skill_ids"] = [item["skill_id"] for item in skill_payload]
        updates["pending_proficiency_skill_ids"] = pending

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
    repo = get_repository()
    updates: dict[str, Any] = {}
    stage = state.get("current_stage", "goal")

    if stage == "goal":
        matched = _match_options(text, role_options())
        if matched and matched[0].id != "role.not_sure":
            role = repo.get_role(matched[0].id) or repo.find_role_by_name(matched[0].label)
            if role:
                updates["target_role"] = role.name
                updates["matched_role_id"] = role.id
                updates["goal"] = state.get("goal") or f"Become a {role.name}"
                updates["goal_summary"] = state.get("goal_summary") or updates["goal"]

    role = repo.get_role(updates.get("matched_role_id") or state.get("matched_role_id"))
    if role and stage == "domain_discovery":
        matched = _match_options(text, domain_options(role))
        domain_ids = list(state.get("selected_domain_ids", []))
        domains = list(state.get("selected_domains", []))
        for option in matched:
            if option.id not in domain_ids:
                domain_ids.append(option.id)
                domains.append(option.label)
        if domain_ids:
            updates["selected_domain_ids"] = domain_ids
            updates["selected_domains"] = domains
            updates["interests"] = list(dict.fromkeys([*state.get("interests", []), *domains]))

    if role and stage == "experience":
        matched = _match_options(text, experience_options(role))
        if matched:
            updates["experience_level"] = _normalize_experience(matched[0].label) or _normalize_experience(
                matched[0].id.split("experience.", 1)[-1]
            )
        elif _normalize_experience(text):
            updates["experience_level"] = _normalize_experience(text)

    if role and stage == "skill_discovery":
        options = skill_options(role)
        matched = _match_options(text, options)
        skill_payload = list(state.get("skills", []))
        pending = list(state.get("pending_proficiency_skill_ids", []))
        if any(option.id == "skill.none_yet" for option in matched) or text.lower() in {
            "none",
            "none yet",
            "no",
            "nope",
        }:
            updates["selected_skill_ids"] = ["skill.none_yet"]
            updates["skills"] = skill_payload
            updates["pending_proficiency_skill_ids"] = []
            updates["current_proficiency_skill_id"] = None
        else:
            for option in matched:
                if option.id == "skill.none_yet":
                    continue
                skill = repo.get_skill(option.id)
                if not skill:
                    continue
                existing = next((item for item in skill_payload if item["skill_id"] == skill.id), None)
                if existing is None:
                    _upsert_skill(skill_payload, skill.id, skill.name, None, "selection")
                    if skill.id not in pending:
                        pending.append(skill.id)
            updates["skills"] = skill_payload
            updates["selected_skill_ids"] = [item["skill_id"] for item in skill_payload]
            updates["pending_proficiency_skill_ids"] = pending

    if stage == "skill_proficiency":
        current_id = state.get("current_proficiency_skill_id") or (
            state.get("pending_proficiency_skill_ids") or [None]
        )[0]
        selected_level = _normalize_level(text)
        if selected_level is None:
            for level in LEVELS:
                if level in text.lower():
                    selected_level = None if level == "none" else level
                    if level == "none":
                        selected_level = "beginner"
                    break
            if "never practiced" in text.lower():
                selected_level = "beginner"
        if selected_level and current_id:
            skill_payload = list(state.get("skills", []))
            skill = repo.get_skill(current_id)
            _upsert_skill(
                skill_payload,
                current_id,
                skill.name if skill else current_id,
                selected_level,
                "confirmed",
            )
            pending = [sid for sid in state.get("pending_proficiency_skill_ids", []) if sid != current_id]
            updates["skills"] = skill_payload
            updates["pending_proficiency_skill_ids"] = pending
            updates["current_proficiency_skill_id"] = pending[0] if pending else None

    if stage == "learning_interests" and text:
        interests = list(dict.fromkeys([*state.get("interests", []), text]))
        updates["interests"] = interests
        updates["specific_interest"] = True

    if stage == "objectives" and text and role:
        matched = _match_options(text, objective_options(role))
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
        f"Target: {state.get('target_role') or 'Not specified'}\n"
        f"Experience: {state.get('experience_level') or 'Not specified'}\n"
        f"Skills: {skill_lines}\n"
        f"Interest: {', '.join(interests) if interests else 'Not specified'}\n"
        f"Objective: {', '.join(objectives) if objectives else 'Not specified'}\n\n"
        "Now I'll identify your skill gaps and build your personalized path."
    )


def _format_gap(gap: dict[str, Any]) -> str:
    def names(items: list[dict[str, Any]]) -> str:
        return ", ".join(item.get("skill_name", "") for item in items) or "None"

    return (
        "Skill gap\n"
        f"Strong: {names(gap.get('strong') or [])}\n"
        f"Developing: {names(gap.get('developing') or [])}\n"
        f"Missing: {names(gap.get('missing') or [])}"
    )


def _prompt(state: LearningState) -> dict[str, Any]:
    role = _role(state)
    missing = _missing(state)

    if "role" in missing:
        family = infer_role_family(" ".join(filter(None, [state.get("goal") or "", _last_user_text(state)])))
        roles = get_repository().roles_in_family(family) if family else get_repository().all_roles()
        if not roles:
            roles = get_repository().all_roles()
        current, total = _progress("goal")
        return {
            "current_stage": "goal",
            "last_reply": "Which direction fits you best?",
            "input_type": "single_select",
            "allow_custom_input": True,
            "options": to_api_options(role_options(roles)),
            "progress_current": current,
            "progress_total": total,
            "missing_information": missing,
            "error": None,
        }

    if "domains" in missing and role:
        current, total = _progress("domain_discovery")
        return {
            "current_stage": "domain_discovery",
            "last_reply": f"Got it — you're aiming to become an {role.name}. Which direction interests you?",
            "input_type": "single_select",
            "allow_custom_input": True,
            "options": to_api_options(domain_options(role)),
            "progress_current": current,
            "progress_total": total,
            "missing_information": missing,
            "error": None,
        }

    if "experience" in missing and role:
        current, total = _progress("experience")
        return {
            "current_stage": "experience",
            "last_reply": "What experience do you have?",
            "input_type": "single_select",
            "allow_custom_input": True,
            "options": to_api_options(experience_options(role)),
            "progress_current": current,
            "progress_total": total,
            "missing_information": missing,
            "error": None,
        }

    if "skills" in missing and role:
        current, total = _progress("skill_discovery")
        return {
            "current_stage": "skill_discovery",
            "last_reply": "Which of these have you explored?",
            "input_type": "multi_select",
            "allow_custom_input": True,
            "options": to_api_options(skill_options(role)),
            "progress_current": current,
            "progress_total": total,
            "missing_information": missing,
            "error": None,
        }

    if "proficiency" in missing:
        pending = list(state.get("pending_proficiency_skill_ids") or [])
        skill = get_repository().get_skill(pending[0]) if pending else None
        current, total = _progress("skill_proficiency")
        return {
            "current_stage": "skill_proficiency",
            "current_proficiency_skill_id": pending[0] if pending else None,
            "last_reply": f"How comfortable are you with {skill.name if skill else 'this skill'}?",
            "input_type": "single_select",
            "allow_custom_input": True,
            "options": to_api_options(proficiency_options(pending[0])) if pending else [],
            "progress_current": current,
            "progress_total": total,
            "missing_information": missing,
            "error": None,
        }

    if "interests" in missing:
        current, total = _progress("learning_interests")
        return {
            "current_stage": "learning_interests",
            "last_reply": "Any specific learning interests?",
            "input_type": "text",
            "allow_custom_input": True,
            "options": [],
            "progress_current": current,
            "progress_total": total,
            "missing_information": missing,
            "error": None,
        }

    if "objectives" in missing and role:
        current, total = _progress("objectives")
        return {
            "current_stage": "objectives",
            "last_reply": "What is your main objective?",
            "input_type": "single_select",
            "allow_custom_input": True,
            "options": to_api_options(objective_options(role)),
            "progress_current": current,
            "progress_total": total,
            "missing_information": missing,
            "error": None,
        }

    current, total = _progress("objectives")
    return {
        "current_stage": "profile_review",
        "profile_complete": True,
        "last_reply": _profile_summary(state),
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
        return {"profile_complete": True, "current_stage": "profile_review"}

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
            after_options.get("current_stage") == "goal" and not after_options.get("matched_role_id")
        )
        
        options = state.get("options") or []
        labels = {str(opt.get("label", "")).lower() for opt in options if isinstance(opt, dict)}
        exact_option = text.lower() in labels or text.lower() in {
            str(opt.get("id", "")).lower() for opt in options if isinstance(opt, dict)
        }
        extraction_updates: dict[str, Any] = {}
        if not exact_option or needs_llm:
            extraction_updates = _apply_extraction(after_options, text)
        merged = _merged(after_options, extraction_updates)
        if merged.get("experience_level") == "none" and not merged.get("skills"):
            merged["pending_proficiency_skill_ids"] = []
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
            "options": [],
        }


def skill_gap_node(state: LearningState) -> dict[str, Any]:
    role_id = state.get("matched_role_id")
    if not role_id:
        return {
            "error": "Could not match a known role to compute a skill gap.",
            "current_stage": "complete",
        }
    result = compute_skill_gap(role_id=role_id, learner_skills=state.get("skills") or [])
    return {
        "skill_gap": result.model_dump(),
        "current_stage": "profile_review",
    }


def generate_learning_path_node(state: LearningState) -> dict[str, Any]:
    gap_data = state.get("skill_gap")
    if not gap_data:
        return {
            "current_stage": "complete",
            "last_reply": state.get("last_reply") or "I could not generate a learning path yet.",
        }
    from app.schemas.path import SkillGapResult

    gap = SkillGapResult.model_validate(gap_data)
    path = generate_learning_path(
        gap,
        interests=state.get("interests") or [],
        objectives=state.get("learning_objectives") or [],
    )
    reply = state.get("last_reply") or _profile_summary(state)
    return {
        "learning_path": path.model_dump(),
        "current_stage": "complete",
        "profile_complete": True,
        "last_reply": f"{reply}\n\n{_format_gap(gap_data)}\n\nYour personalized learning path is ready.",
        "input_type": "complete",
        "allow_custom_input": False,
        "options": [],
        "missing_information": [],
        "error": None,
    }
