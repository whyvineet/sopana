from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import GoalType

Proficiency = Literal["beginner", "basic", "intermediate", "advanced", "expert"]
ExperienceLevel = Literal["none", "casual", "workshop", "project", "professional"]

IntentType = Literal[
    "greeting",                                                  
    "casual",                                   
    "partial_goal",                                                               
                                                                                       
    "vague_goal",                                                              
                                                                      
    "valid_goal",                                                  
                                                                        
    "answer",                                                        
    "clarification",                                                     
    "off_topic",                                                                            
]

class IntentAnalysis(BaseModel):
    intent: IntentType = "off_topic"
    goal_type: GoalType = "unresolved"
    goal: str | None = None
    is_valid_goal: bool = False
    needs_clarification: bool = True
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    extracted_role: str | None = None
    conversational_reply: str | None = None
    clarification_reason: str | None = None
    all_missing_profile_fields: list[str] = Field(default_factory=list)

class SkillEvidence(BaseModel):
    skill_name: str
    level: Proficiency | None = None

class LearnerExtraction(BaseModel):
    goal_summary: str | None = None
    goal_type: GoalType = "unresolved"

    target_role: str | None = None
    role_confidence: Literal["low", "medium", "high"] = "low"

    industry: str | None = None
    function: str | None = None
    specialization: str | None = None
    career_intent: Literal["professional", "personal", "unclear"] | None = None

    domains: list[str] = Field(default_factory=list)
    experience_level: ExperienceLevel | None = None
    skills: list[SkillEvidence] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    learning_objectives: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
