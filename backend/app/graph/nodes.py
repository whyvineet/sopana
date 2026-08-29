from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from app.graph.extract import build_learner_profile_json, extract_from_history
from app.graph.intent import (
    CONFIDENCE_THRESHOLD,
    classify_intent,
    get_clarification_reply,
)
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
    "skill_proficiency",
    "learning_interests",
    "objectives",
]

EXPERIENCE_ALIASES = {
                              
    "none": "none",
    "nil": "none",
    "nothing": "none",
    "n/a": "none",
    "na": "none",
    "no": "none",
    "nope": "none",
    "not applicable": "none",
    "no experience": "none",
    "no_experience": "none",
    "never": "none",
    "never done": "none",
    "never programmed": "none",
    "just starting": "none",
    "complete beginner": "none",
    "total beginner": "none",
    "no_hands_on_experience": "none",
            
    "casual": "beginner",
    "coursework": "beginner",
    "tutorials": "beginner",
    "self_taught": "beginner",
    "self-taught": "beginner",
    "hobby": "beginner",
    "beginner": "beginner",
              
    "beginner_projects": "intermediate",
    "beginner__projects": "intermediate",
    "workshop": "intermediate",
    "workshops": "intermediate",
    "bootcamp": "intermediate",
             
    "project": "intermediate",
    "projects": "intermediate",
    "academic_projects": "intermediate",
    "academic__projects": "intermediate",
    "built_a_few_projects": "intermediate",
    "side projects": "intermediate",
    "personal projects": "intermediate",
    "intermediate": "intermediate",
                  
    "professional": "advanced",
    "professional_experience": "advanced",
    "professional__experience": "advanced",
    "work experience": "advanced",
    "job experience": "advanced",
    "industry": "advanced",
    "employed": "advanced",
    "expert": "advanced",
    "advanced": "advanced",
}

def _last_user_text(state: LearningState) -> str:
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage) and isinstance(msg.content, str):
            return msg.content.strip()
    return ""

def _missing(state: LearningState) -> list[str]:
                                                                          
    goal_status = state.get("goal_status", "unresolved")
    goal_type = state.get("goal_type", "unresolved")
    if goal_status != "confirmed":
        return ["role"] if goal_type == "career" else ["goal"]

    missing: list[str] = []
    if not state.get("experience_level"):
        missing.append("experience")
    if not state.get("selected_skill_ids") and state.get("experience_level") != "none":
        missing.append("skills")
    elif any(s.get("level") == "pending" for s in state.get("skills", [])):
        missing.append("skill_proficiency")
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

    orig = value.strip().lower()
    if orig in EXPERIENCE_ALIASES:
        return EXPERIENCE_ALIASES[orig]

    for alias, mapped in EXPERIENCE_ALIASES.items():
        if alias in orig:
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
            current_level = item.get("level")
            
            if source == "nlp_inference":
                next_level = current_level if current_level else (level or "pending")
            elif source == "selection":
                next_level = level if level else (current_level or "pending")
            else:
                next_level = level or current_level or "pending"
                
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
            "level": level or "pending",
            "source": source,
        }
    )

def _apply_history_extraction(state: LearningState, allow_role_update: bool = False) -> dict[str, Any]:
    messages = state.get("messages", [])
    if not messages:
        return {}

    current_profile: dict[str, Any] = {
        "target_role": state.get("target_role"),
        "industry": state.get("industry"),
        "function": state.get("function"),
        "specialization": state.get("specialization"),
        "career_intent": state.get("career_intent"),
        "experience_level": state.get("experience_level"),
        "skills": state.get("skills", []),
        "interests": state.get("interests", []),
        "learning_objectives": state.get("learning_objectives", []),
        "goal_type": state.get("goal_type"),
    }

    parsed = extract_from_history(messages, current_profile)
    updates: dict[str, Any] = {}

    if parsed.goal_summary and not state.get("goal"):
        updates["goal"] = parsed.goal_summary
        updates["goal_summary"] = parsed.goal_summary

    if parsed.goal_type and parsed.goal_type != "unresolved" and state.get("goal_type") in ("unresolved", None):
        updates["goal_type"] = parsed.goal_type

    if allow_role_update:
                                                                                 
        if parsed.industry and not state.get("industry"):
            updates["industry"] = parsed.industry
        if parsed.function and not state.get("function"):
            updates["function"] = parsed.function
        if parsed.specialization and not state.get("specialization"):
            updates["specialization"] = parsed.specialization
        if parsed.career_intent and parsed.career_intent != "unclear" and not state.get("career_intent"):
            updates["career_intent"] = parsed.career_intent

        if parsed.target_role and parsed.role_confidence in ("medium", "high") and not state.get("target_role"):
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

    if parsed.contradictions:
        existing = list(state.get("detected_contradictions", []))
        merged = list(dict.fromkeys([*existing, *parsed.contradictions]))
        updates["detected_contradictions"] = merged
        logger.info("Contradictions detected: %s", parsed.contradictions)

    return updates

def _apply_option_text(state: LearningState, text: str) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    stage = state.get("current_stage", "goal")

    if stage == "experience":
                                   
        matched = _match_options(text, experience_options())
        if matched:
            normalized = _normalize_experience(matched[0].label) or _normalize_experience(
                matched[0].id.split("experience.", 1)[-1]
            )
            if normalized:
                updates["experience_level"] = normalized
        else:
                                                                                    
            normalized = _normalize_experience(text)
            if normalized:
                updates["experience_level"] = normalized
            elif text.lower().strip() in {"nothing", "nil", "none", "nope", "no", "n/a", "na", "never"}:
                                                                       
                updates["experience_level"] = "none"

    if stage == "skill_discovery":
        skill_payload = list(state.get("skills", []))
        normalized_text = text.lower().strip()
        if normalized_text in {"none", "none yet", "no", "nope", "nothing", "nil", "no skills", "n/a"}:
            updates["selected_skill_ids"] = ["skill.none_yet"]
            updates["skills"] = skill_payload
        elif text:
            parts = [p.strip() for p in text.split(",")]
            for part in parts:
                if part:
                    _upsert_skill(skill_payload, part, None, "selection")
            updates["skills"] = skill_payload
            updates["selected_skill_ids"] = [item["skill_id"] for item in skill_payload]

    if stage == "skill_proficiency" and text:
        import json
        skill_payload = list(state.get("skills", []))
        try:
            parsed_ratings = json.loads(text)
            if isinstance(parsed_ratings, list):
                for rating in parsed_ratings:
                    skill_id = rating.get("skill_id")
                    level = rating.get("level")
                    if skill_id and level:
                        for s in skill_payload:
                            if s.get("skill_id") == skill_id:
                                s["level"] = level.lower()
            updates["skills"] = skill_payload
        except Exception:
            logger.warning("Failed to parse skill proficiency ratings: %s", text)

    if stage == "learning_interests" and text:
        normalized_text = text.lower().strip()
        if normalized_text not in {"none", "no", "nope", "nil", "nothing", "n/a"}:
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

    role_parts: list[str] = []
    if state.get("specialization"):
        role_parts.append(state["specialization"])
    if state.get("function") and state.get("function") not in (state.get("specialization") or ""):
        role_parts.append(state["function"])
    role_display = (
        state.get("target_role")
        or (", ".join(role_parts) if role_parts else "Not specified")
    )
    industry_display = state.get("industry") or "Not specified"
    career_intent = state.get("career_intent") or "Not specified"

    return (
        "Here's what I've learned about you:\n\n"
        f"Goal: {state.get('goal_summary') or state.get('goal') or 'Not specified'}\n"
        f"Target Role: {role_display}\n"
        f"Industry: {industry_display}\n"
        f"Career Intent: {career_intent.title()}\n"
        f"Experience: {state.get('experience_level') or 'Not specified'}\n"
        f"Skills: {skill_lines}\n"
        f"Interests: {', '.join(interests) if interests else 'Not specified'}\n"
        f"Objective: {', '.join(objectives) if objectives else 'Not specified'}\n\n"
        "Now I'll research your role and build a personalized learning path."
    )

def _prompt(state: LearningState) -> dict[str, Any]:
    missing = _missing(state)

    if "goal" in missing or "role" in missing:
        current, total = _progress("goal")
        return {
            "current_stage": "goal",
            "last_reply": "What would you like to learn or achieve?",
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

    if "skill_proficiency" in missing:
        pending_skills = [s for s in state.get("skills", []) if s.get("level") == "pending"]
        if pending_skills:
            current, total = _progress("skill_proficiency")
            return {
                "current_stage": "skill_proficiency",
                "last_reply": "How would you rate your proficiency in these skills?",
                "input_type": "skill_proficiency",
                "allow_custom_input": False,
                "options": [{"id": s["skill_id"], "label": s["name"]} for s in pending_skills],
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
                                                                               
        profile_json = build_learner_profile_json(dict(state))
        return {
            "current_stage": "profile_review",
            "profile_complete": True,
            "learner_profile_json": profile_json,
            "last_reply": _profile_summary(state) + "\n\nResearching your role and resources... This may take a minute.",
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
    result = _conversation_node_impl(state)
    if "last_reply" in result and result["last_reply"]:
        if "messages" not in result:
            result["messages"] = [AIMessage(content=result["last_reply"])]
    return result

def _conversation_node_impl(state: LearningState) -> dict[str, Any]:
    if state.get("profile_complete") or state.get("current_stage") in {"profile_review", "complete"}:
        if not state.get("profile_complete"):
            return {**_prompt(state), "profile_complete": True}
        return {"profile_complete": True}

    text = _last_user_text(state)
    if not text:
        current, total = _progress("goal")
        return {
            "current_stage": "goal",
            "last_reply": "What would you like to learn or achieve?",
            "input_type": "text",
            "allow_custom_input": True,
            "options": [],
            "progress_current": current,
            "progress_total": total,
            "missing_information": ["goal"],
            "error": None,
        }

    try:
        messages = state.get("messages", [])
        clarification_count = state.get("clarification_count", 0)
        goal_status = state.get("goal_status", "unresolved")

        state_snapshot: dict[str, Any] = {
            "target_role": state.get("target_role"),
            "goal": state.get("goal"),
            "experience_level": state.get("experience_level"),
            "skills": state.get("skills", []),
            "interests": state.get("interests", []),
            "learning_objectives": state.get("learning_objectives", []),
            "clarification_count": clarification_count,
        }

        intent = classify_intent(messages, state_snapshot, text)

        logger.info(
            "goal_status=%s | msg='%s...' | intent=%s is_valid=%s role=%s confidence=%.2f",
            goal_status,
            text[:40],
            intent.intent,
            intent.is_valid_goal,
            intent.extracted_role,
            intent.confidence,
        )

        _CLARIFICATION_INTENTS = {"greeting", "casual", "off_topic", "vague_goal", "partial_goal"}

        if goal_status != "confirmed":
                                                                          
            if intent.is_valid_goal:
                                                                          
                goal_updates: dict[str, Any] = {
                    "goal_status": "confirmed",
                    "goal_intent": intent.intent,
                    "goal_confidence": intent.confidence,
                    "goal_needs_clarification": False,
                    "clarification_count": clarification_count,
                    "goal_type": intent.goal_type,
                }
                if intent.extracted_role:
                    goal_updates["target_role"] = intent.extracted_role
                if intent.goal:
                    goal_updates["goal"] = intent.goal
                    goal_updates["goal_summary"] = intent.goal

                after_goal = _merged(state, goal_updates)

                extraction_updates = _apply_history_extraction(after_goal, allow_role_update=True)
                merged = _merged(after_goal, extraction_updates)

                prompt = _prompt(merged)
                result = {k: v for k, v in merged.items() if k != "messages"}
                result.update(prompt)
                return result

            else:
                                                                          
                reply = get_clarification_reply(intent, clarification_count)
                new_goal_status = "clarifying" if intent.intent == "partial_goal" else "unresolved"
                current, total = _progress("goal")
                return {
                    "current_stage": "goal",
                    "goal_status": new_goal_status,
                    "last_reply": reply,
                    "input_type": "text",
                    "allow_custom_input": True,
                    "options": [],
                    "progress_current": current,
                    "progress_total": total,
                    "missing_information": ["role"] if intent.goal_type == "career" else ["goal"],
                    "clarification_count": clarification_count + 1,
                    "goal_intent": intent.intent,
                    "goal_confidence": intent.confidence,
                    "goal_needs_clarification": True,
                    "goal_type": intent.goal_type,
                    "error": None,
                }

        option_updates = _apply_option_text(state, text)
        after_options = _merged(state, option_updates)

        extraction_updates = _apply_history_extraction(after_options, allow_role_update=True)

        contradiction_update: dict[str, Any] = {}
        new_contradictions = extraction_updates.get("detected_contradictions", [])
        if new_contradictions:
            existing = list(state.get("detected_contradictions", []))
            merged_contradictions = list(dict.fromkeys([*existing, *new_contradictions]))
            contradiction_update["detected_contradictions"] = merged_contradictions

        intent_updates: dict[str, Any] = {
            "goal_intent": intent.intent,
            "goal_confidence": intent.confidence,
            "goal_needs_clarification": False,
            "goal_type": intent.goal_type,
        }

        merged = _merged(after_options, extraction_updates, contradiction_update, intent_updates)
        prompt = _prompt(merged)
        result = {k: v for k, v in merged.items() if k != "messages"}
        result.update(prompt)

        if new_contradictions and result.get("last_reply"):
            contradiction_notice = (
                "I noticed some conflicting information in our conversation:\n"
                + "\n".join(f"- {c}" for c in new_contradictions[:2])
                + "\n\nI'll proceed with the most recent information. Let me know if anything needs correcting.\n\n"
            )
            result["last_reply"] = contradiction_notice + result["last_reply"]

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
