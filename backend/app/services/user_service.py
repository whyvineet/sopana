from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.core.supabase import get_supabase
from app.schemas.auth import UserProfileResponse

_TABLE = "users"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_profile(row: dict[str, Any]) -> UserProfileResponse:
    return UserProfileResponse(
        id=row["id"],
        name=row.get("name", ""),
        email=row.get("email", ""),
        onboarding_completed=row.get("onboarding_completed", False),
        onboarding_step=row.get("onboarding_step", "profile"),
        app_state=row.get("app_state"),
        last_route=row.get("last_route", "/start-onboarding"),
        session_id=row.get("session_id"),
        created_at=str(row["created_at"]) if row.get("created_at") else None,
        updated_at=str(row["updated_at"]) if row.get("updated_at") else None,
    )


def get_profile(user_id: str) -> UserProfileResponse | None:
    sb = get_supabase()
    result = sb.table(_TABLE).select("*").eq("id", user_id).single().execute()
    if not result.data:
        return None
    return _row_to_profile(result.data)


def get_or_create_profile(
    user_id: str, name: str = "", email: str = ""
) -> UserProfileResponse:
    sb = get_supabase()
    result = sb.table(_TABLE).select("*").eq("id", user_id).execute()
    if result.data:
        return _row_to_profile(result.data[0])

    now = _now_iso()
    row = {
        "id": user_id,
        "name": name,
        "email": email,
        "onboarding_completed": False,
        "onboarding_step": "profile",
        "app_state": None,
        "last_route": "/start-onboarding",
        "session_id": None,
        "created_at": now,
        "updated_at": now,
    }
    insert_result = sb.table(_TABLE).insert(row).execute()
    return _row_to_profile(insert_result.data[0])


def update_profile(user_id: str, data: dict[str, Any]) -> UserProfileResponse:
    sb = get_supabase()
    data["updated_at"] = _now_iso()
    result = sb.table(_TABLE).update(data).eq("id", user_id).execute()
    return _row_to_profile(result.data[0])


def save_app_state(
    user_id: str,
    app_state: dict[str, Any],
    last_route: str | None = None,
    session_id: str | None = None,
) -> UserProfileResponse:
    payload: dict[str, Any] = {"app_state": app_state}
    if last_route is not None:
        payload["last_route"] = last_route
    if session_id is not None:
        payload["session_id"] = session_id
    return update_profile(user_id, payload)


def update_onboarding_step(
    user_id: str,
    onboarding_step: str,
    extra: dict[str, Any] | None = None,
) -> UserProfileResponse:
    payload: dict[str, Any] = {"onboarding_step": onboarding_step}
    if extra:
        payload.update(extra)
    return update_profile(user_id, payload)


def complete_onboarding(
    user_id: str, extra: dict[str, Any] | None = None
) -> UserProfileResponse:
    payload: dict[str, Any] = {
        "onboarding_completed": True,
        "onboarding_step": "complete",
    }
    if extra:
        payload.update(extra)
    return update_profile(user_id, payload)
