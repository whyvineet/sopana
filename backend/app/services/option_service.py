from __future__ import annotations

from dataclasses import dataclass

from app.knowledge.repository import Role, get_repository


@dataclass
class OptionItem:
    id: str
    label: str


def _slugify(label: str) -> str:
    cleaned = (
        label.strip()
        .lower()
        .replace("&", "and")
        .replace("/", " ")
        .replace("-", " ")
        .replace(",", " ")
    )
    return "_".join(cleaned.split())


def role_options(roles: list[Role] | None = None) -> list[OptionItem]:
    repo = get_repository()
    source = roles if roles is not None else repo.all_roles()
    items = [OptionItem(id=role.id, label=role.name) for role in source]
    items.append(OptionItem(id="role.not_sure", label="Not sure"))
    return items


def domain_options(role: Role) -> list[OptionItem]:
    return [OptionItem(id=f"domain.{_slugify(name)}", label=name) for name in role.domains]


def experience_options(role: Role) -> list[OptionItem]:
    values = role.experience_options or [
        "None",
        "Beginner projects",
        "Academic projects",
        "Professional experience",
    ]
    return [OptionItem(id=f"experience.{_slugify(name)}", label=name) for name in values]


def objective_options(role: Role) -> list[OptionItem]:
    values = role.learning_objective_options or [
        "Build fundamentals",
        "Get job-ready",
        "Build projects",
        "Something else",
    ]
    return [OptionItem(id=f"objective.{_slugify(name)}", label=name) for name in values]


def skill_options(role: Role) -> list[OptionItem]:
    repo = get_repository()
    items: list[OptionItem] = []
    seen: set[str] = set()
    for req in role.required_skills:
        skill = repo.get_skill(req.skill_id)
        if not skill or skill.id in seen:
            continue
        items.append(OptionItem(id=skill.id, label=skill.name))
        seen.add(skill.id)
    items.append(OptionItem(id="skill.none_yet", label="None yet"))
    return items


def proficiency_options(skill_id: str) -> list[OptionItem]:
    return [
        OptionItem(id=f"{skill_id}::beginner", label="Beginner"),
        OptionItem(id=f"{skill_id}::basic", label="Basic"),
        OptionItem(id=f"{skill_id}::intermediate", label="Intermediate"),
        OptionItem(id=f"{skill_id}::advanced", label="Advanced"),
    ]


def to_api_options(items: list[OptionItem]) -> list[dict[str, str]]:
    return [{"id": item.id, "label": item.label} for item in items]
