from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Proficiency = Literal["beginner", "basic", "intermediate", "advanced", "expert"]
ExperienceLevel = Literal["none", "casual", "workshop", "project", "professional"]


class SkillEvidence(BaseModel):
    skill_name: str
    level: Proficiency | None = None


class LearnerExtraction(BaseModel):
    goal_summary: str | None = None
    target_role: str | None = None
    role_confidence: Literal["low", "medium", "high"] = "low"
    domains: list[str] = Field(default_factory=list)
    experience_level: ExperienceLevel | None = None
    skills: list[SkillEvidence] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    learning_objectives: list[str] = Field(default_factory=list)
