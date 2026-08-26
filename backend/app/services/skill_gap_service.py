from __future__ import annotations

from typing import Any

from app.knowledge.repository import get_repository, level_rank
from app.schemas.path import SkillGapItem, SkillGapResult


def _learner_levels(learner_skills: list[dict[str, Any]]) -> dict[str, str]:
    repo = get_repository()
    result: dict[str, str] = {}
    for claim in learner_skills:
        skill = repo.get_skill(claim.get("skill_id")) or repo.find_skill_by_name(claim.get("name", ""))
        if not skill:
            continue
        current = result.get(skill.id)
        claimed_level = claim.get("level") or "beginner"
        if current is None or level_rank(claimed_level) > level_rank(current):
            result[skill.id] = claimed_level
    return result


def compute_skill_gap(role_id: str, learner_skills: list[dict[str, Any]]) -> SkillGapResult:
    repo = get_repository()
    role = repo.get_role(role_id)
    if not role:
        raise ValueError(f"Unknown role_id: {role_id}")

    learner_levels = _learner_levels(learner_skills)
    strong: list[SkillGapItem] = []
    developing: list[SkillGapItem] = []
    missing: list[SkillGapItem] = []

    for req in role.required_skills:
        skill = repo.get_skill(req.skill_id)
        if not skill:
            continue
        current_level = learner_levels.get(req.skill_id, "none")
        current_rank = level_rank(current_level)
        item = SkillGapItem(
            skill_id=skill.id,
            skill_name=skill.name,
            required_level=req.min_level,
            current_level=current_level,
            status="missing",
        )
        if current_rank == 0:
            missing.append(item)
        elif current_rank >= level_rank(req.min_level):
            item.status = "strong"
            strong.append(item)
        else:
            item.status = "developing"
            developing.append(item)

    total = len(strong) + len(developing) + len(missing)
    explanation = (
        f"You're already strong in {len(strong)} of {total} skills {role.name} needs. "
        f"{len(developing)} are developing, and {len(missing)} are still missing."
        if total
        else f"No required skills are configured for {role.name}."
    )
    return SkillGapResult(
        role_id=role.id,
        role_name=role.name,
        strong=strong,
        developing=developing,
        missing=missing,
        explanation=explanation,
    )
