from __future__ import annotations

from typing import Annotated, Any, Literal, TypedDict

from langgraph.graph.message import add_messages

StageName = Literal[
    "goal",
    "domain_discovery",
    "experience",
    "skill_discovery",
    "skill_proficiency",
    "learning_interests",
    "objectives",
    "profile_review",
    "complete",
]


class SkillEvidence(TypedDict):
    skill_id: str
    name: str
    level: str
    source: str


class ConversationOption(TypedDict):
    id: str
    label: str


class LearningState(TypedDict):
    messages: Annotated[list, add_messages]
    session_id: str
    current_stage: StageName
    profile_complete: bool

    goal: str | None
    goal_summary: str | None
    target_role: str | None
    selected_domains: list[str]
    selected_domain_ids: list[str]
    experience_level: str | None
    interests: list[str]
    specific_interest: bool
    skills: list[SkillEvidence]
    selected_skill_ids: list[str]
    pending_proficiency_skill_ids: list[str]
    current_proficiency_skill_id: str | None
    learning_objectives: list[str]
    missing_information: list[str]

    last_reply: str
    input_type: str
    allow_custom_input: bool
    options: list[ConversationOption]
    progress_current: int
    progress_total: int

    skill_gap: dict[str, Any] | None
    learning_path: dict[str, Any] | None
    error: str | None

    research_status: Literal["idle", "in_progress", "complete", "failed"]
    role_research: dict[str, Any] | None
    skill_requirements: list[dict[str, Any]]
    candidate_path: dict[str, Any] | None
    researched_resources: list[dict[str, Any]]


def initial_state(session_id: str) -> LearningState:
    return LearningState(
        messages=[],
        session_id=session_id,
        current_stage="goal",
        profile_complete=False,
        goal=None,
        goal_summary=None,
        target_role=None,
        selected_domains=[],
        selected_domain_ids=[],
        experience_level=None,
        interests=[],
        specific_interest=False,
        skills=[],
        selected_skill_ids=[],
        pending_proficiency_skill_ids=[],
        current_proficiency_skill_id=None,
        learning_objectives=[],
        missing_information=["goal", "role", "domains", "experience", "skills", "objectives"],
        last_reply="",
        input_type="text",
        allow_custom_input=True,
        options=[],
        progress_current=1,
        progress_total=7,
        skill_gap=None,
        learning_path=None,
        error=None,
        research_status="idle",
        role_research=None,
        skill_requirements=[],
        candidate_path=None,
        researched_resources=[],
    )
