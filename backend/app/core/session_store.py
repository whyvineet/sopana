from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

_STORE_PATH = Path(__file__).parent.parent.parent / ".sessions.json"
_lock = threading.Lock()


class SessionStore:
    def __init__(self, path: Path = _STORE_PATH) -> None:
        self._path = path
        self._data: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text())
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def _flush(self) -> None:
        try:
            self._path.write_text(json.dumps(self._data, default=str))
        except OSError:
            pass

    def get(self, session_id: str) -> dict[str, Any] | None:
        with _lock:
            return self._data.get(session_id)

    def set(self, session_id: str, state: dict[str, Any]) -> None:
        with _lock:
            self._data[session_id] = state
            self._flush()

    def exists(self, session_id: str) -> bool:
        with _lock:
            return session_id in self._data


_store: SessionStore | None = None


def get_session_store() -> SessionStore:
    global _store
    if _store is None:
        _store = SessionStore()
    return _store
