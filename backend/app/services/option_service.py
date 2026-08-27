from __future__ import annotations

from dataclasses import dataclass

from app.schemas.research import RoleResearch, SkillRequirement


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


def domain_options(research: RoleResearch | None = None) -> list[OptionItem]:
    domains = research.specializations if research and research.specializations else [
        "Web Development",
        "Data Science",
        "Systems Engineering",
        "Cloud Architecture",
    ]
    return [OptionItem(id=f"domain.{_slugify(name)}", label=name) for name in domains]


def experience_options() -> list[OptionItem]:
    values = [
        "None",
        "Beginner projects",
        "Academic projects",
        "Professional experience",
    ]
    return [OptionItem(id=f"experience.{_slugify(name)}", label=name) for name in values]


def objective_options() -> list[OptionItem]:
    values = [
        "Build fundamentals",
        "Get job-ready",
        "Build projects",
        "Something else",
    ]
    return [OptionItem(id=f"objective.{_slugify(name)}", label=name) for name in values]


def skill_options(requirements: list[SkillRequirement] | None = None) -> list[OptionItem]:
    items: list[OptionItem] = []
    seen: set[str] = set()
    
    if requirements:
        for req in requirements:
            skill_name = req.skill.strip()
            skill_id = f"dynamic.{_slugify(skill_name)}"
            if skill_id in seen:
                continue
            items.append(OptionItem(id=skill_id, label=skill_name))
            seen.add(skill_id)
            
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
