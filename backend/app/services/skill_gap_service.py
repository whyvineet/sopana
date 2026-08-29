from __future__ import annotations

from typing import Any

from app.schemas.path import SkillGapItem, SkillGapResult
from app.schemas.research import SkillRequirement

LEVELS = ["none", "beginner", "basic", "intermediate", "advanced", "expert"]
LEVEL_RANK = {level: i for i, level in enumerate(LEVELS)}


def level_rank(level: str | None) -> int:
    if not level:
        return 0
    return LEVEL_RANK.get(level.lower(), 0)


def _level_name(level_int: int) -> str:
    _map = {
        1: "awareness",
        2: "beginner",
        3: "intermediate",
        4: "advanced",
        5: "expert"
    }
    return _map.get(level_int, "intermediate")


def _learner_levels(learner_skills: list[dict[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for claim in learner_skills:
        skill_name = claim.get("name") or claim.get("label") or claim.get("skill")
        if not skill_name:
            continue
        skill_name = skill_name.strip().lower()
        claimed_level = claim.get("level") or "beginner"
        
        current = result.get(skill_name)
        if current is None or level_rank(claimed_level) > level_rank(current):
            result[skill_name] = claimed_level
    return result


def compute_dynamic_skill_gap(
    goal_name: str,
    requirements: list[SkillRequirement],
    learner_skills: list[dict[str, Any]],
) -> SkillGapResult:
    learner_levels = _learner_levels(learner_skills)
    strong: list[SkillGapItem] = []
    developing: list[SkillGapItem] = []
    missing: list[SkillGapItem] = []

    for req in requirements:
        skill_key = req.skill.strip().lower()
        required_level_str = _level_name(req.required_level)
        
        current_level = learner_levels.get(skill_key, "none")
        current_rank = level_rank(current_level)
        
        item = SkillGapItem(
            skill_id=f"dynamic.{skill_key}",
            skill_name=req.skill,
            required_level=required_level_str,
            current_level=current_level,
            status="missing",
        )
        if current_rank == 0:
            missing.append(item)
        elif current_rank >= level_rank(required_level_str):
            item.status = "strong"
            strong.append(item)
        else:
            item.status = "developing"
            developing.append(item)

    total = len(strong) + len(developing) + len(missing)
    explanation = (
        f"You're already strong in {len(strong)} of {total} skills/concepts needed for {goal_name}. "
        f"{len(developing)} are developing, and {len(missing)} are still missing."
        if total
        else f"No required skills/concepts were found for {goal_name}."
    )
    
    return SkillGapResult(
        goal_id=f"dynamic.{goal_name.lower().replace(' ', '_')}",
        goal_name=goal_name,
        strong=strong,
        developing=developing,
        missing=missing,
        explanation=explanation,
    )
