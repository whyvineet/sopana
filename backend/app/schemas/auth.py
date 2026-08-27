from __future__ import annotations

from typing import Any

from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class RefreshRequest(BaseModel):
    refresh_token: str


class UserProfileResponse(BaseModel):
    id: str
    name: str
    email: str
    onboarding_completed: bool = False
    onboarding_step: str = "profile"
    app_state: dict[str, Any] | None = None
    last_route: str = "/start-onboarding"
    session_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict[str, Any]
    profile: UserProfileResponse


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"



class AppState(BaseModel):
    session_id: str | None = None
    messages: list[dict[str, Any]] = []
    stage: dict[str, Any] | None = None
    answers: list[Any] = []
    learner_profile: dict[str, Any] | None = None
    missing_information: list[Any] = []
    skill_gap: dict[str, Any] | None = None
    learning_path: dict[str, Any] | None = None
    dashboard: dict[str, Any] | None = None
    conversation_complete: bool = False


class SaveAppStateRequest(BaseModel):
    app_state: AppState
    last_route: str | None = None
    session_id: str | None = None


class UpdateOnboardingStepRequest(BaseModel):
    onboarding_step: str
    session_id: str | None = None


class CompleteOnboardingRequest(BaseModel):
    data: dict[str, Any] = {}
