from __future__ import annotations

from pydantic import BaseModel, Field


class SkillGapItem(BaseModel):
    skill_id: str
    skill_name: str
    required_level: str
    current_level: str
    status: str


class SkillGapResult(BaseModel):
    role_id: str = ""
    role_name: str = ""
    strong: list[SkillGapItem] = Field(default_factory=list)
    developing: list[SkillGapItem] = Field(default_factory=list)
    missing: list[SkillGapItem] = Field(default_factory=list)
    explanation: str | None = None


class ResourceRef(BaseModel):
    id: str
    title: str
    type: str
    url: str | None = None
    description: str | None = None
    difficulty: str | None = None
    estimated_duration: str | None = None
    provider: str | None = None
    skill_ids: list[str] = Field(default_factory=list)
    source_url: str | None = None
    reason: str | None = None
    is_verified: bool = False


class ProjectRef(BaseModel):
    id: str
    title: str
    description: str
    skill_ids: list[str] = Field(default_factory=list)


class LearningStep(BaseModel):
    id: str
    title: str
    description: str
    status: str = "upcoming"
    completed: bool = False
    skills: list[str]
    prerequisites: list[str]
    duration: str
    resources: list[ResourceRef] = Field(default_factory=list)
    project: ProjectRef | None = None
    reason: str | None = None
    milestone: str | None = None
    expected_outcome: str | None = None
    explanation: str | None = None


class LearningPath(BaseModel):
    role_id: str = ""
    role_name: str
    steps: list[LearningStep]
    overall_progress: float
    current_focus_step_id: str | None = None
    explanation: str | None = None
