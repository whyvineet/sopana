from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.core.supabase import get_supabase
from app.schemas.auth import UserProfileResponse

_TABLE = "users"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_profile(row: dict[str, Any], paths: list[dict[str, Any]] = None) -> UserProfileResponse:
    if paths is None:
        paths = []
    
    active_id = row.get("active_session_id") or row.get("session_id")
    app_state = None
    if active_id:
        active_path = next((p for p in paths if p["session_id"] == active_id), None)
        if active_path:
            app_state = active_path.get("app_state")
    
    if not app_state:
        app_state = row.get("app_state")

    learning_paths = []
    for p in paths:
        target = None
        if p.get("app_state") and isinstance(p["app_state"], dict):
            profile = p["app_state"].get("learner_profile") or {}
            target = profile.get("target_role") or profile.get("target") or profile.get("role_name")
        learning_paths.append({
            "session_id": p["session_id"],
            "target_role": target,
            "created_at": p.get("created_at"),
            "updated_at": p.get("updated_at"),
        })

    return UserProfileResponse(
        id=row["id"],
        name=row.get("name", ""),
        email=row.get("email", ""),
        onboarding_completed=row.get("onboarding_completed", False),
        onboarding_step=row.get("onboarding_step", "profile"),
        app_state=app_state,
        last_route=row.get("last_route", "/start-onboarding"),
        session_id=active_id,
        active_session_id=active_id,
        learning_paths=learning_paths,
        created_at=str(row["created_at"]) if row.get("created_at") else None,
        updated_at=str(row["updated_at"]) if row.get("updated_at") else None,
    )


def get_profile(user_id: str) -> UserProfileResponse | None:
    sb = get_supabase()
    result = sb.table(_TABLE).select("*").eq("id", user_id).single().execute()
    if not result.data:
        return None
    
    paths_result = sb.table("learning_paths").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
    paths = paths_result.data if paths_result.data else []
    return _row_to_profile(result.data, paths)


def get_or_create_profile(
    user_id: str, name: str = "", email: str = ""
) -> UserProfileResponse:
    sb = get_supabase()
    result = sb.table(_TABLE).select("*").eq("id", user_id).execute()
    if result.data:
        paths_result = sb.table("learning_paths").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
        paths = paths_result.data if paths_result.data else []
        return _row_to_profile(result.data[0], paths)

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
        "active_session_id": None,
        "created_at": now,
        "updated_at": now,
    }
    insert_result = sb.table(_TABLE).insert(row).execute()
    return _row_to_profile(insert_result.data[0], [])


def update_profile(user_id: str, data: dict[str, Any]) -> UserProfileResponse:
    sb = get_supabase()
    data["updated_at"] = _now_iso()
    result = sb.table(_TABLE).update(data).eq("id", user_id).execute()
    
    paths_result = sb.table("learning_paths").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
    paths = paths_result.data if paths_result.data else []
    return _row_to_profile(result.data[0], paths)


def save_app_state(
    user_id: str,
    app_state: dict[str, Any],
    last_route: str | None = None,
    session_id: str | None = None,
) -> UserProfileResponse:
    sb = get_supabase()
    
    if session_id:
        now = _now_iso()
        sb.table("learning_paths").upsert({
            "session_id": session_id,
            "user_id": user_id,
            "app_state": app_state,
            "updated_at": now
        }).execute()
        
    payload: dict[str, Any] = {}
    if last_route is not None:
        payload["last_route"] = last_route
    if session_id is not None:
        payload["active_session_id"] = session_id
        payload["app_state"] = app_state
        payload["session_id"] = session_id
        
    if payload:
        return update_profile(user_id, payload)
    
    return get_profile(user_id)


def update_active_session(user_id: str, session_id: str) -> UserProfileResponse:
    return update_profile(user_id, {"active_session_id": session_id, "session_id": session_id})


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
