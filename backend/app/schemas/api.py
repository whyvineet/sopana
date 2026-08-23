from __future__ import annotations

from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    session_id: str
    message: str = Field(default="", max_length=2000)
    selected_options: list[str] = Field(default_factory=list)


class ConversationOption(BaseModel):
    id: str
    label: str


class ProgressInfo(BaseModel):
    current: int
    total: int


class ConversationResponse(BaseModel):
    session_id: str
    stage: str
    reply: str
    input_type: str = "text"
    options: list[ConversationOption] = Field(default_factory=list)
    allow_custom_input: bool = True
    suggested_options: list[str] = Field(default_factory=list)
    profile: dict
    onboarding_complete: bool
    progress: ProgressInfo | None = None
    missing_information: list[str] = Field(default_factory=list)
    skill_gap: dict | None = None
    learning_path: dict | None = None
    error: str | None = None
