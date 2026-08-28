from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.session_store import get_session_store
from app.integrations.llm.openrouter import get_chat_model
from app.schemas.research import FeedbackPayload

logger = logging.getLogger(__name__)

_STRUGGLING_CONFIDENCE = 2                                
_MASTERED_CONFIDENCE = 5                       
_STRUGGLING_SCORE = 50.0                                            
_MASTERED_SCORE = 85.0                                            

def _classify_performance(feedback: FeedbackPayload) -> str:
    confidence = feedback.confidence
    score = feedback.assessment_score

    if score is not None:
        if confidence <= _STRUGGLING_CONFIDENCE or score <= _STRUGGLING_SCORE:
            return "struggling"
        if confidence >= _MASTERED_CONFIDENCE and score >= _MASTERED_SCORE:
            return "mastered"
        return "progressing"

    if confidence <= _STRUGGLING_CONFIDENCE:
        return "struggling"
    if confidence >= _MASTERED_CONFIDENCE:
        return "mastered"
    return "progressing"

def _generate_adaptive_recommendation(
    step: dict[str, Any],
    performance: str,
    feedback: FeedbackPayload,
    learner_profile: dict[str, Any],
) -> str:
    step_title = step.get("title", "this step")
    step_skills = ", ".join(step.get("skills") or [])
    step_description = step.get("description") or "No description."
    target_role = learner_profile.get("target_role") or "their target role"
    experience = learner_profile.get("experience_level") or "not specified"

    prompt = f"""You are SOPĀNA, an adaptive AI learning advisor.
A learner just completed a step in their personalized learning path.
Generate a SHORT, specific, encouraging adaptive recommendation (2-3 sentences max).

## Step completed:
- Title: {step_title}
- Skills covered: {step_skills}
- Description: {step_description}

## Learner feedback:
- Confidence (1=lost, 5=mastered): {feedback.confidence}/5
- Assessment score: {f"{feedback.assessment_score:.0f}%" if feedback.assessment_score is not None else "Not taken"}
- Time spent: {f"{feedback.time_spent_minutes} minutes" if feedback.time_spent_minutes else "Not recorded"}
- Notes: {feedback.notes or "None"}

## Learner context:
- Target role: {target_role}
- Experience level: {experience}

## Performance classification: {performance}

Based on this, generate:
- For "struggling": Suggest reviewing fundamentals, specific easier resources, or practice exercises
- For "mastered": Acknowledge the achievement, suggest they can move faster or skip basic reinforcement
- For "progressing": Encourage continuing and briefly note the next logical focus

Keep it personal, specific to the step content, and encouraging. Do not be generic."""

    try:
        llm = get_chat_model()
        response = llm.invoke([
            SystemMessage(content="You are SOPĀNA, an expert adaptive learning advisor. Be concise and encouraging."),
            HumanMessage(content=prompt),
        ])
        return str(response.content).strip()
    except Exception as exc:
        logger.error("LLM adaptive recommendation failed: %s", exc)
                                 
        if performance == "struggling":
            return (
                f"It looks like {step_title} was challenging. "
                "We recommend revisiting the fundamentals before moving on — "
                "taking a bit more time here will make the next steps much easier."
            )
        if performance == "mastered":
            return (
                f"Excellent work on {step_title}! You've clearly got a strong grasp of this. "
                "We'll adjust the path to focus on more advanced content in upcoming steps."
            )
        return (
            f"Good progress on {step_title}! Keep up the momentum — "
            "you're on the right track toward your goal."
        )

def _get_remedial_resources(step: dict[str, Any]) -> list[dict[str, Any]]:
    resources = step.get("resources") or []
    beginner_resources = [
        r for r in resources
        if isinstance(r, dict) and r.get("difficulty") in ("beginner", None)
    ]

    if beginner_resources:
        return beginner_resources[:2]

    skills = step.get("skills") or []
    return [
        {
            "title": f"Beginner guide to {skill}",
            "url": f"https://google.com/search?q=beginner+guide+{skill.replace(' ', '+')}",
            "type": "search",
            "difficulty": "beginner",
            "reason": f"Foundational resource for {skill}",
        }
        for skill in skills[:2]
    ]

def process_feedback(session_id: str, step_id: str, feedback: FeedbackPayload) -> dict[str, Any]:
    store = get_session_store()
    stored = store.get(session_id)
    if not stored:
        raise ValueError("Session not found")

    learning_path = stored.get("learning_path")
    if not learning_path:
        raise ValueError("Learning path not found")

    steps = learning_path.get("steps", [])
    step = next((s for s in steps if isinstance(s, dict) and s.get("id") == step_id), None)

    if not step:
        raise ValueError("Step not found")

    feedback_record = feedback.model_dump()
    step["feedback"] = feedback_record

    feedback_history = list(stored.get("learner_feedback_history", []))
    feedback_history.append({
        "step_id": step_id,
        "step_title": step.get("title"),
        "step_skills": step.get("skills", []),
        **feedback_record,
    })
    stored["learner_feedback_history"] = feedback_history
    stored["learning_path"] = learning_path

    store.set(session_id, stored)

    performance = _classify_performance(feedback)

    learner_profile: dict[str, Any] = {
        "target_role": stored.get("target_role"),
        "experience_level": stored.get("experience_level"),
    }

    adaptive_message = _generate_adaptive_recommendation(step, performance, feedback, learner_profile)

    result: dict[str, Any] = {
        "status": "adapted",
        "performance": performance,
        "message": adaptive_message,
    }

    if performance == "struggling":
        remedial = _get_remedial_resources(step)
        if remedial:
            result["remedial_resources"] = remedial
        result["recommendation"] = "revisit"

    elif performance == "mastered":
        result["recommendation"] = "advance"
        result["can_skip_reinforcement"] = True

    else:
        result["recommendation"] = "continue"
        result["status"] = "recorded"

    return result
