from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from app.integrations.llm.openrouter import get_chat_model
from app.schemas.profile import IntentAnalysis
from app.prompts import render_template

logger = logging.getLogger(__name__)

_MAX_HISTORY_MESSAGES = 14
CONFIDENCE_THRESHOLD = 0.55

def _format_history_for_prompt(messages: list[BaseMessage]) -> str:
    recent = messages[-_MAX_HISTORY_MESSAGES:] if len(messages) > _MAX_HISTORY_MESSAGES else messages
    lines: list[str] = []
    for msg in recent:
        role = "User" if isinstance(msg, HumanMessage) else "Sopana"
        content = str(msg.content).strip()
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines) if lines else "(No conversation history yet)"

def classify_intent(
    messages: list[BaseMessage],
    state_snapshot: dict[str, Any],
    latest_text: str,
) -> IntentAnalysis:
    llm = get_chat_model().with_structured_output(IntentAnalysis)

    history_str = _format_history_for_prompt(messages)
    clarification_count = state_snapshot.get("clarification_count", 0)

    prompt_content = render_template(
        "intent_classification.jinja",
        history_str=history_str,
        profile=state_snapshot,
        latest_text=latest_text,
        clarification_count=clarification_count,
    )

    try:
        result: IntentAnalysis = llm.invoke([
            HumanMessage(content=prompt_content),
        ])
        logger.info(
            "Intent: intent=%s is_valid=%s role=%s needs_clarification=%s confidence=%.2f",
            result.intent,
            result.is_valid_goal,
            result.extracted_role,
            result.needs_clarification,
            result.confidence,
        )
        return result
    except Exception as exc:
        logger.error("Intent classification failed: %s", exc)
        return IntentAnalysis(
            intent="off_topic",
            goal=None,
            is_valid_goal=False,
            needs_clarification=True,
            confidence=0.0,
            extracted_role=None,
            conversational_reply="Could you tell me what you'd like to learn or which career you're aiming for?",
        )

def get_clarification_reply(
    intent: IntentAnalysis,
    clarification_count: int,
) -> str:
                                                              
    if intent.conversational_reply and intent.conversational_reply.strip():
        return intent.conversational_reply.strip()

    if intent.intent == "greeting":
        return (
            "Hi! I'm SOPANA, your AI learning advisor. "
            "What would you like to learn or what career are you aiming for?"
        )
    if intent.intent == "casual":
        return "Happy to help! What would you like to learn or work toward?"
    if intent.intent == "partial_goal":
        goal_hint = intent.goal or "that area"
        return f"Interesting direction! Could you tell me a bit more about what you'd like to achieve with {goal_hint}?"
    if intent.intent == "vague_goal":
        return (
            "Could you tell me a bit more about what area interests you? "
            "For example: technology, creative arts, business, science, or something else?"
        )
    if intent.intent == "off_topic":
        if clarification_count >= 2:
            return (
                "I'm here to help you build a personalized learning path. "
                "What career or skill would you like to develop?"
            )
        return (
            "What would you like to learn or become? "
            "For example: a software engineer, a data scientist, or a graphic designer."
        )
                      
    return "Could you tell me a bit more about what you'd like to learn or achieve?"
