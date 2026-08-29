from __future__ import annotations

import uuid
from typing import Any

from app.schemas.path import (
    LearningPath,
    LearningStep,
    ResourceRef,
    SkillGapResult,
)
from app.schemas.research import CandidatePath, LearningResource


def _resource_ref(res: LearningResource) -> ResourceRef:
    return ResourceRef(
        id=f"res_{uuid.uuid4().hex[:8]}",
        title=res.title,
        type=res.type,
        url=res.url,
        description=res.reason,
        difficulty=res.difficulty,
        estimated_duration=res.estimated_duration,
        provider=res.provider,
        skill_ids=res.skills,
        source_url=res.source_url,
        reason=res.reason,
        is_verified=res.is_verified,
    )


def build_dynamic_learning_path(
    gap: SkillGapResult,
    candidate: CandidatePath,
    resources: list[LearningResource],
) -> LearningPath:

    resources_by_skill: dict[str, list[LearningResource]] = {}
    for res in resources:
        for skill in res.skills:
            skill_key = skill.strip().lower()
            resources_by_skill.setdefault(skill_key, []).append(res)
            
    steps: list[LearningStep] = []
    
    for i, step in enumerate(candidate.steps):
        skill_key = step.skill.strip().lower()
        
        step_resources = resources_by_skill.get(skill_key, [])
        resource_refs = [_resource_ref(r) for r in step_resources]
        
        steps.append(
            LearningStep(
                id=f"step_{uuid.uuid4().hex[:8]}",
                title=f"Master {step.skill}",
                description=step.reason,
                status="current" if i == 0 else "upcoming",
                completed=False,
                skills=[step.skill],
                prerequisites=step.prerequisites,
                duration=step.estimated_duration,
                resources=resource_refs,
                reason=step.reason,
                milestone=step.milestone,
                expected_outcome=step.expected_outcome,
                explanation=step.explanation,
                project=step.project,
            )
        )

    total_steps = len(steps)
    completed_steps = sum(1 for s in steps if s.completed)
    overall_progress = round(completed_steps / total_steps, 2) if total_steps else 0.0

    return LearningPath(
        goal_id=gap.goal_id,
        goal_name=gap.goal_name,
        steps=steps,
        overall_progress=overall_progress,
        current_focus_step_id=steps[0].id if steps else None,
        explanation=candidate.overall_rationale or gap.explanation,
    )
