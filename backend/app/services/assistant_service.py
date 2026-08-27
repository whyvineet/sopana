from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.session_store import get_session_store
from app.integrations.llm.openrouter import get_chat_model

logger = logging.getLogger(__name__)


def handle_chat(session_id: str, message: str, context_step_id: str | None = None) -> str:
    store = get_session_store()
    stored = store.get(session_id)
    if not stored:
        raise ValueError("Session not found")
        
    profile = {
        "goal": stored.get("goal"),
        "role": stored.get("target_role"),
        "experience": stored.get("experience_level"),
        "skills": stored.get("skills"),
    }
    
    context = "No specific step context."
    if context_step_id and stored.get("learning_path"):
        steps = stored["learning_path"].get("steps", [])
        step = next((s for s in steps if s.get("id") == context_step_id), None)
        if step:
            context = f"The learner is asking about the step: {step.get('title')}. Description: {step.get('description')}."

    system_prompt = f"""You are SOPĀNA, an expert AI learning assistant.
Help the learner with their question based on their profile and current learning context.
Be encouraging, concise, and highly relevant.

Learner Profile:
Goal: {profile['goal']}
Target Role: {profile['role']}
Experience: {profile['experience']}

Context:
{context}
"""

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
