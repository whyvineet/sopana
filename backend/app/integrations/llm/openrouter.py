from __future__ import annotations

from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.core.config import get_settings


class LLMConfigurationError(RuntimeError):
    pass


@lru_cache
def get_chat_model() -> ChatOpenAI:
    settings = get_settings()
    if not settings.openrouter_api_key:
        raise LLMConfigurationError(
            "OPENROUTER_API_KEY is not set. Copy backend/.env.example to backend/.env and add your key."
        )
    app_title = settings.openrouter_app_title.encode("ascii", "ignore").decode("ascii")
    return ChatOpenAI(
        model=settings.openrouter_model,
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.2,
        max_tokens=1024,
        default_headers={
            "HTTP-Referer": settings.openrouter_http_referer,
            "X-Title": app_title,
        },
    )
