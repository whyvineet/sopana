from __future__ import annotations

import json
import logging
import time
from typing import Any

from app.schemas.research import GoalResearch

logger = logging.getLogger(__name__)

_KEY_PREFIX = "__research_cache__"


def _normalize_role_key(role: str) -> str:
    return role.strip().lower().replace(" ", "_")


class ResearchCache:
    def __init__(self, ttl_hours: int = 24) -> None:
        self._ttl_seconds = ttl_hours * 3600

    def _store(self):
        from app.core.session_store import get_session_store
        return get_session_store()

    def _key(self, role: str) -> str:
        return f"{_KEY_PREFIX}{_normalize_role_key(role)}"

    def get_role_research(self, role: str) -> GoalResearch | None:
        store = self._store()
        raw: dict[str, Any] | None = store.get_raw(self._key(role))
        if raw is None:
            return None
        cached_at = raw.get("cached_at", 0)
        if time.time() - cached_at > self._ttl_seconds:
            logger.debug("Research cache expired for role: %s", role)
            return None
        try:
            return GoalResearch.model_validate(raw["data"])
        except Exception as exc:
            logger.warning("Research cache deserialize error: %s", exc)
            return None

    def set_role_research(self, role: str, research: GoalResearch) -> None:
        store = self._store()
        store.set_raw(
            self._key(role),
            {"cached_at": time.time(), "data": research.model_dump()},
        )


_cache: ResearchCache | None = None


def get_research_cache() -> ResearchCache:
    global _cache
    if _cache is None:
        from app.core.config import get_settings
        _cache = ResearchCache(ttl_hours=get_settings().research_cache_ttl_hours)
    return _cache
