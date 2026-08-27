from __future__ import annotations

from typing import Any

from supabase import AuthApiError

from app.core.supabase import get_supabase
from app.schemas.auth import AuthResponse, TokenResponse
from app.services import user_service


def _build_auth_response(session: Any, user: Any) -> AuthResponse:
    profile = user_service.get_or_create_profile(
        user_id=user.id,
        name=user.user_metadata.get("full_name", user.user_metadata.get("name", "")),
        email=user.email or "",
    )
    return AuthResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "name": profile.name,
        },
        profile=profile,
    )


def signup(name: str, email: str, password: str) -> AuthResponse:
    sb = get_supabase()
    try:
        user = sb.auth.admin.create_user(
            {
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"full_name": name},
            }
        )
        response = sb.auth.sign_in_with_password({"email": email, "password": password})
    except AuthApiError as exc:
        raise ValueError(str(exc)) from exc

    if not response.session or not response.user:
        raise ValueError("Could not get a session after account creation.")


    user_service.get_or_create_profile(
        user_id=response.user.id,
        name=name,
        email=email,
    )

    user_service.update_profile(response.user.id, {"name": name, "email": email})

    return _build_auth_response(response.session, response.user)


def login(email: str, password: str) -> AuthResponse:
    sb = get_supabase()
    try:
        response = sb.auth.sign_in_with_password({"email": email, "password": password})
    except AuthApiError as exc:
        raise ValueError(str(exc)) from exc

    return _build_auth_response(response.session, response.user)


def reset_password(email: str) -> None:
    sb = get_supabase()
    try:
        sb.auth.reset_password_email(email)
    except AuthApiError as exc:
        raise ValueError(str(exc)) from exc


def refresh_token(refresh_tok: str) -> TokenResponse:
    sb = get_supabase()
    try:
        response = sb.auth.refresh_session(refresh_tok)
    except AuthApiError as exc:
        raise ValueError(str(exc)) from exc
    return TokenResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
    )


def logout(access_token: str) -> None:
    sb = get_supabase()
    try:
        sb.auth.admin.sign_out(access_token)
    except Exception:  
        pass  
