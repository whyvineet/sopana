from __future__ import annotations

import logging

from app.core.session_store import get_session_store
from app.schemas.research import FeedbackPayload

logger = logging.getLogger(__name__)


def process_feedback(session_id: str, step_id: str, feedback: FeedbackPayload) -> dict:
    store = get_session_store()
    stored = store.get(session_id)
    if not stored:
        raise ValueError("Session not found")
        
    learning_path = stored.get("learning_path")
    if not learning_path:
        raise ValueError("Learning path not found")
        
    steps = learning_path.get("steps", [])
    step = next((s for s in steps if s.get("id") == step_id), None)
    
    if not step:
        raise ValueError("Step not found")
        
    step["feedback"] = feedback.model_dump()
    store.set(session_id, stored)
    
    if feedback.confidence <= 2:
        return {
            "status": "adapted",
            "message": "It looks like you found that difficult. We'll suggest some fundamental resources to help reinforce this skill."
        }
    elif feedback.confidence == 5:
        return {
            "status": "adapted",
            "message": "Great job! You mastered this quickly. We'll adjust future steps to be slightly more challenging."
        }
        
    return {
        "status": "recorded",
        "message": "Feedback recorded. Keep up the good work!"
    }
