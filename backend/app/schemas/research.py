from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.path import ProjectRef


class Source(BaseModel):
    title: str = ""
    url: str = ""
    domain: str | None = None
    snippet: str | None = None


class GoalResearch(BaseModel):
    goal: str = ""
    description: str = ""
    core_topics: list[str] = Field(default_factory=list)
    optional_topics: list[str] = Field(default_factory=list)
    tools_and_methods: list[str] = Field(default_factory=list)
    practical_applications: list[str] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    searched_at: str | None = None


class SkillRequirement(BaseModel):
    skill: str
    importance: Literal["essential", "important", "optional"] = "important"
    required_level: int = Field(default=3, ge=1, le=5)
    prerequisites: list[str] = Field(default_factory=list)
    description: str | None = None
    evidence: list[str] = Field(default_factory=list)


class SkillRequirementsOutput(BaseModel):
    skill_requirements: list[SkillRequirement] = Field(default_factory=list)

class LearningResource(BaseModel):
    title: str
    url: str | None = None
    provider: str | None = None
    type: Literal[
        "course", "book", "tutorial", "documentation",
        "video", "project", "article", "other"
    ] = "course"
    skills: list[str] = Field(default_factory=list)
    difficulty: Literal["beginner", "intermediate", "advanced"] = "intermediate"
    estimated_duration: str | None = None
    prerequisites: list[str] = Field(default_factory=list)
    source_url: str | None = None
    reason: str | None = None
    is_verified: bool = False


class LearningResourcesOutput(BaseModel):
    resources: list[LearningResource] = Field(default_factory=list)


class CandidatePathStep(BaseModel):
    skill: str
    prerequisites: list[str] = Field(default_factory=list)
    reason: str = ""
    milestone: str | None = None
    expected_outcome: str | None = None
    estimated_duration: str = "~2 weeks"
    explanation: str | None = None
    project: ProjectRef | None = None


class CandidatePath(BaseModel):
    steps: list[CandidatePathStep] = Field(default_factory=list)
    overall_rationale: str | None = None


class FeedbackPayload(BaseModel):
    confidence: int = Field(ge=1, le=5, description="1=lost, 5=mastered")
    assessment_score: float | None = Field(default=None, ge=0, le=100)
    time_spent_minutes: int | None = None
    notes: str | None = None
