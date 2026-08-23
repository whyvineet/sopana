from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.integrations.llm.openrouter import get_chat_model
from app.schemas.profile import LearnerExtraction


def extract_learner_details(text: str) -> LearnerExtraction:
    llm = get_chat_model().with_structured_output(LearnerExtraction)
    prompt = (
        "Extract structured learner information from the message. "
        "Identify the target role and mentioned skills autonomously from the context. "
        "Only set a proficiency level when the message gives evidence (years, projects, confidence). "
        "Use experience_level none | casual | workshop | project | professional. "
        "Set role_confidence to low when the goal is broad (for example 'work in AI') "
        "and high only when a specific role is clear."
    )
    return llm.invoke([SystemMessage(content=prompt), HumanMessage(content=text)])



def infer_role_family(text: str) -> str | None:
    t = text.lower()
    if any(word in t for word in ("actor", "acting", "theatre", "theater", "film", "audition")):
        return "performing_arts"
    if any(word in t for word in ("security", "cyber", "soc", "threat")):
        return "security"
    if any(word in t for word in ("frontend", "react", "ui", "css")):
        return "software"
    if any(word in t for word in ("backend", "api", "server")):
        return "software"
    if any(word in t for word in ("ai", "ml", "machine learning", "data scien", "deep learning")):
        return "ai"
    return None
