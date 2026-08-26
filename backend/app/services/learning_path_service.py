from __future__ import annotations

from app.knowledge.repository import Project, get_repository
from app.schemas.path import (
    LearningPath,
    LearningStep,
    ProjectRef,
    ResourceRef,
    SkillGapResult,
)

_DIFFICULTY_DURATION = {
    "beginner": "~1 week",
    "basic": "~1 week",
    "intermediate": "~2 weeks",
    "advanced": "~3 weeks",
    "expert": "~4 weeks",
}
_DEFAULT_DIFFICULTY = "beginner"


def _difficulty_for(required_level: str | None) -> str:
    return required_level if required_level in _DIFFICULTY_DURATION else _DEFAULT_DIFFICULTY


def _resource_refs(skill_id: str) -> list[ResourceRef]:
    repo = get_repository()
    return [
        ResourceRef(
            id=resource.id,
            title=resource.title,
            type=resource.type,
            url=resource.url,
            description=resource.description,
            difficulty=resource.difficulty,
            estimated_duration=resource.estimated_duration,
            provider=resource.provider,
            skill_ids=resource.skill_ids,
        )
        for resource in repo.resources_for_skill(skill_id)
    ]


def _project_ref(project: Project) -> ProjectRef:
    return ProjectRef(
        id=project.id,
        title=project.title,
        description=project.description,
        skill_ids=project.skill_ids,
    )


def _skill_step_title(name: str, status: str) -> str:
    if status == "developing":
        return f"Strengthen {name}" if name.lower() != "machine learning" else "Machine Learning Fundamentals"
    return "Machine Learning Fundamentals" if name.lower() == "machine learning" else name


def generate_learning_path(
    gap: SkillGapResult,
    interests: list[str] | None = None,
    objectives: list[str] | None = None,
) -> LearningPath:
    repo = get_repository()
    phrases = [*(interests or []), *(objectives or [])]

    status_by_skill: dict[str, str] = {}
    required_level_by_skill: dict[str, str] = {}
    for item in [*gap.strong, *gap.developing, *gap.missing]:
        status_by_skill[item.skill_id] = item.status
        required_level_by_skill[item.skill_id] = item.required_level
    role_skill_ids = set(status_by_skill.keys())

    matched_projects = repo.match_projects(phrases, role_skill_ids)
    for project in matched_projects:
        for skill_id in project.skill_ids:
            status_by_skill.setdefault(skill_id, "missing")

    to_process = list(status_by_skill.keys())
    while to_process:
        skill_id = to_process.pop()
        skill = repo.get_skill(skill_id)
        if not skill:
            continue
        for prereq_id in skill.prerequisites:
            if prereq_id not in status_by_skill:
                status_by_skill[prereq_id] = "missing"
                to_process.append(prereq_id)

    skills_to_learn = [sid for sid, status in status_by_skill.items() if status != "strong"]
    ordered_ids = repo.topological_order(skills_to_learn)

    steps: list[LearningStep] = []
    covered = {item.skill_id for item in gap.strong}
    used_project_ids: set[str] = set()

    for skill_id in ordered_ids:
        skill = repo.get_skill(skill_id)
        if not skill:
            continue

        status = status_by_skill.get(skill_id, "missing")
        difficulty = _difficulty_for(required_level_by_skill.get(skill_id))
        steps.append(
            LearningStep(
                id=f"skill_{skill_id}",
                title=_skill_step_title(skill.name, status),
                description=f"Master {skill.name} to progress towards your goal.",
                status="upcoming",
                completed=False,
                skills=[skill_id],
                prerequisites=[
                    repo.get_skill(prereq_id).name if repo.get_skill(prereq_id) else prereq_id
                    for prereq_id in skill.prerequisites
                ],
                duration=_DIFFICULTY_DURATION[difficulty],
                resources=_resource_refs(skill_id),
            )
        )
        covered.add(skill_id)

        for project in matched_projects:
            if project.id in used_project_ids:
                continue
            if project.skill_ids and set(project.skill_ids) <= covered:
                used_project_ids.add(project.id)
                steps.append(
                    LearningStep(
                        id=f"project_{project.id}",
                        title=project.title,
                        description=project.description,
                        status="upcoming",
                        completed=False,
                        skills=project.skill_ids,
                        prerequisites=[
                            repo.get_skill(sid).name if repo.get_skill(sid) else sid
                            for sid in project.skill_ids
                        ],
                        duration="~1 week",
                        project=_project_ref(project),
                    )
                )

    for project in matched_projects:
        if project.id not in used_project_ids:
            steps.append(
                LearningStep(
                    id=f"project_{project.id}",
                    title=project.title,
                    description=project.description,
                    status="upcoming",
                    completed=False,
                    skills=project.skill_ids,
                    prerequisites=[
                        repo.get_skill(sid).name if repo.get_skill(sid) else sid
                        for sid in project.skill_ids
                    ],
                    duration="~1 week",
                    project=_project_ref(project),
                )
            )

    total_steps = len(steps)
    completed_steps = len([step for step in steps if step.completed])
    overall_progress = round(completed_steps / total_steps, 2) if total_steps else 0.0

    if steps:
        steps[0].status = "current"
        steps[0].completed = False

    return LearningPath(
        role_id=gap.role_id,
        role_name=gap.role_name,
        steps=steps,
        overall_progress=overall_progress,
        current_focus_step_id=steps[0].id if steps else None,
        explanation=gap.explanation,
    )
