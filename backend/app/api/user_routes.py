from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.auth import CurrentUser
from app.schemas.auth import (
    CompleteOnboardingRequest,
    SaveAppStateRequest,
    UpdateOnboardingStepRequest,
    UserProfileResponse,
)
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


def _user_id(user: CurrentUser) -> str:
    uid = user.get("sub")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token: missing sub claim.")
    return uid


@router.get("/me", response_model=UserProfileResponse)
def get_me(user: CurrentUser) -> UserProfileResponse:
    uid = _user_id(user)
    profile = user_service.get_profile(uid)
    if not profile:
        email = user.get("email", "")
        name = user.get("user_metadata", {}).get("full_name", "") if isinstance(user.get("user_metadata"), dict) else ""
        profile = user_service.get_or_create_profile(uid, name=name, email=email)
    return profile


@router.put("/me/app-state", response_model=UserProfileResponse)
def save_app_state(payload: SaveAppStateRequest, user: CurrentUser) -> UserProfileResponse:
    uid = _user_id(user)
    try:
        return user_service.save_app_state(
            user_id=uid,
            app_state=payload.app_state.model_dump(),
            last_route=payload.last_route,
            session_id=payload.session_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not save app state: {exc}") from exc


@router.put("/me/onboarding-step", response_model=UserProfileResponse)
def update_onboarding_step(
    payload: UpdateOnboardingStepRequest, user: CurrentUser
) -> UserProfileResponse:
    uid = _user_id(user)
    try:
        extra = {}
        if payload.session_id is not None:
            extra["session_id"] = payload.session_id
        return user_service.update_onboarding_step(uid, payload.onboarding_step, extra or None)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not update onboarding step: {exc}") from exc


@router.post("/me/complete-onboarding", response_model=UserProfileResponse)
def complete_onboarding(
    payload: CompleteOnboardingRequest, user: CurrentUser
) -> UserProfileResponse:
    uid = _user_id(user)
    try:
        return user_service.complete_onboarding(uid, payload.data or None)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not complete onboarding: {exc}") from exc
