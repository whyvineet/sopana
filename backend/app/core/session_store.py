from __future__ import annotations

import logging
import threading
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class AbstractSessionStore(ABC):
    @abstractmethod
    def get(self, session_id: str) -> dict[str, Any] | None: ...

    @abstractmethod
    def set(self, session_id: str, state: dict[str, Any]) -> None: ...

    @abstractmethod
    def exists(self, session_id: str) -> bool: ...

    @abstractmethod
    def delete(self, session_id: str) -> None: ...


class InMemorySessionStore(AbstractSessionStore):

    def __init__(self) -> None:
        self._data: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, session_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._data.get(session_id)

    def set(self, session_id: str, state: dict[str, Any]) -> None:
        with self._lock:
            self._data[session_id] = state

    def exists(self, session_id: str) -> bool:
        with self._lock:
            return session_id in self._data

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._data.pop(session_id, None)

    def get_raw(self, key: str) -> dict[str, Any] | None:
        return self.get(key)

    def set_raw(self, key: str, value: dict[str, Any]) -> None:
        self.set(key, value)


class SupabaseSessionStore(AbstractSessionStore):

    _TABLE = "sessions"

    def __init__(self) -> None:
        from app.core.supabase import get_supabase
        self._sb = get_supabase()

    def get(self, session_id: str) -> dict[str, Any] | None:
        try:
            result = (
                self._sb.table(self._TABLE)
                .select("state")
                .eq("id", session_id)
                .execute()
            )
            if result.data:
                return result.data[0]["state"]
        except Exception as exc:
            logger.error("SupabaseSessionStore.get failed: %s", exc)
        return None

    def set(self, session_id: str, state: dict[str, Any]) -> None:
        try:
            self._sb.table(self._TABLE).upsert(
                {"id": session_id, "state": state}
            ).execute()
        except Exception as exc:
            logger.error("SupabaseSessionStore.set failed: %s", exc)

    def exists(self, session_id: str) -> bool:
        try:
            result = (
                self._sb.table(self._TABLE)
                .select("id")
                .eq("id", session_id)
                .execute()
            )
            return bool(result.data)
        except Exception as exc:
            logger.error("SupabaseSessionStore.exists failed: %s", exc)
            return False

    def delete(self, session_id: str) -> None:
        try:
            self._sb.table(self._TABLE).delete().eq("id", session_id).execute()
        except Exception as exc:
            logger.error("SupabaseSessionStore.delete failed: %s", exc)

    def get_raw(self, key: str) -> dict[str, Any] | None:
        return self.get(key)

    def set_raw(self, key: str, value: dict[str, Any]) -> None:
        self.set(key, value)


_store: AbstractSessionStore | None = None
_store_lock = threading.Lock()


def get_session_store() -> AbstractSessionStore:
    global _store
    if _store is not None:
        return _store
    with _store_lock:
        if _store is not None:
            return _store
        from app.core.config import get_settings
        settings = get_settings()
        if settings.supabase_configured:
            try:
                _store = SupabaseSessionStore()
                logger.info("Using Supabase session store")
            except Exception as exc:
                logger.warning("Supabase session store init failed (%s); using in-memory fallback", exc)
                _store = InMemorySessionStore()
        else:
            logger.warning(
                "SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not configured — "
                "using in-memory session store (data lost on restart)"
            )
            _store = InMemorySessionStore()
        return _store
