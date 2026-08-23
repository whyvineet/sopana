"""Canonical knowledge layer: roles, skills, prerequisites, resources, projects.

This is deliberately static, deterministic prototype data (see spec section
"KNOWLEDGE LAYER" — structured prototype data is fine; the LLM must never
invent role requirements, skills, prerequisites, or resources). Swap this
module for a real ESCO/O*NET-backed store later without touching callers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

LEVELS = ["none", "beginner", "basic", "intermediate", "advanced", "expert"]
LEVEL_RANK = {level: i for i, level in enumerate(LEVELS)}


def level_rank(level: str | None) -> int:
    if not level:
        return 0
    return LEVEL_RANK.get(level.lower(), 0)


@dataclass
class Skill:
    id: str
    name: str
    category: str
    prerequisites: list[str] = field(default_factory=list)


@dataclass
class RequiredSkill:
    skill_id: str
    min_level: str


@dataclass
class Role:
    id: str
    name: str
    description: str
    family: str
    required_skills: list[RequiredSkill]
    domains: list[str] = field(default_factory=list)
    experience_options: list[str] = field(default_factory=list)
    learning_objective_options: list[str] = field(default_factory=list)


@dataclass
class Resource:
    id: str
    title: str
    type: str
    skill_ids: list[str]
    url: str | None
    description: str | None = None
    difficulty: str | None = None
    estimated_duration: str | None = None
    provider: str | None = None


@dataclass
class Project:
    id: str
    title: str
    description: str
    skill_ids: list[str]
    keywords: list[str] = field(default_factory=list)


def _skill(id_: str, name: str, category: str, prerequisites: list[str] | None = None) -> Skill:
    return Skill(id=id_, name=name, category=category, prerequisites=prerequisites or [])


def _req(skill_id: str, min_level: str) -> RequiredSkill:
    return RequiredSkill(skill_id=skill_id, min_level=min_level)


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------
_SKILLS: list[Skill] = [
    # AI / ML family
    _skill("skill.python", "Python", "ai"),
    _skill("skill.statistics", "Statistics", "ai"),
    _skill("skill.machine_learning", "Machine Learning", "ai", ["skill.statistics"]),
    _skill("skill.deep_learning", "Deep Learning", "ai", ["skill.machine_learning"]),
    _skill("skill.generative_ai", "Generative AI", "ai", ["skill.deep_learning"]),
    _skill("skill.model_deployment", "Model Deployment", "ai", ["skill.python"]),
    _skill("skill.mlops", "MLOps", "ai", ["skill.model_deployment"]),
    _skill("skill.data_wrangling", "Data Wrangling", "ai", ["skill.python"]),
    _skill("skill.data_visualization", "Data Visualization", "ai", ["skill.statistics"]),
    # Performing arts family
    _skill("skill.acting_techniques", "Acting Techniques", "performing_arts"),
    _skill("skill.method_acting", "Method Acting", "performing_arts", ["skill.acting_techniques"]),
    _skill("skill.screen_acting", "Screen Acting", "performing_arts", ["skill.acting_techniques"]),
    _skill("skill.voice_diction", "Voice & Diction", "performing_arts"),
    _skill("skill.body_language", "Body Language", "performing_arts"),
    _skill("skill.improvisation", "Improvisation", "performing_arts", ["skill.acting_techniques"]),
    _skill(
        "skill.audition_preparation",
        "Audition Preparation",
        "performing_arts",
        ["skill.acting_techniques", "skill.voice_diction"],
    ),
    # Software family
    _skill("skill.programming_fundamentals", "Programming Fundamentals", "software"),
    _skill("skill.data_structures", "Data Structures & Algorithms", "software", ["skill.programming_fundamentals"]),
    _skill("skill.apis", "Building APIs", "software", ["skill.programming_fundamentals"]),
    _skill("skill.system_design", "System Design", "software", ["skill.data_structures"]),
    _skill("skill.testing", "Testing", "software", ["skill.programming_fundamentals"]),
    # Security family
    _skill("skill.networking_fundamentals", "Networking Fundamentals", "security"),
    _skill("skill.security_fundamentals", "Security Fundamentals", "security"),
    _skill(
        "skill.threat_detection",
        "Threat Detection",
        "security",
        ["skill.networking_fundamentals", "skill.security_fundamentals"],
    ),
    _skill("skill.incident_response", "Incident Response", "security", ["skill.threat_detection"]),
]

# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------
_AI_OBJECTIVES = [
    "Ship production AI systems",
    "Build a portfolio of ML projects",
    "Get job-ready as an AI professional",
    "Something else",
]
_ACTOR_OBJECTIVES = [
    "Land professional acting roles",
    "Build an audition-ready reel",
    "Develop stage presence",
    "Something else",
]

_ROLES: list[Role] = [
    Role(
        id="role.ai_engineer",
        name="AI Engineer",
        description="Builds and ships production AI systems end to end.",
        family="ai",
        domains=["Machine Learning", "Deep Learning", "Generative AI", "Computer Vision", "NLP", "MLOps"],
        learning_objective_options=_AI_OBJECTIVES,
        required_skills=[
            _req("skill.python", "intermediate"),
            _req("skill.statistics", "basic"),
            _req("skill.machine_learning", "intermediate"),
            _req("skill.deep_learning", "beginner"),
            _req("skill.generative_ai", "beginner"),
            _req("skill.model_deployment", "intermediate"),
            _req("skill.mlops", "beginner"),
        ],
    ),
    Role(
        id="role.ml_engineer",
        name="ML Engineer",
        description="Designs, trains, and deploys machine learning models at scale.",
        family="ai",
        domains=["Machine Learning", "Model Deployment", "MLOps", "Data Engineering"],
        learning_objective_options=_AI_OBJECTIVES,
        required_skills=[
            _req("skill.python", "intermediate"),
            _req("skill.statistics", "intermediate"),
            _req("skill.machine_learning", "advanced"),
            _req("skill.model_deployment", "intermediate"),
            _req("skill.mlops", "intermediate"),
        ],
    ),
    Role(
        id="role.data_scientist",
        name="Data Scientist",
        description="Turns raw data into insights and predictive models.",
        family="ai",
        domains=["Statistics", "Machine Learning", "Data Visualization", "Data Wrangling"],
        learning_objective_options=_AI_OBJECTIVES,
        required_skills=[
            _req("skill.python", "intermediate"),
            _req("skill.statistics", "advanced"),
            _req("skill.data_wrangling", "intermediate"),
            _req("skill.data_visualization", "intermediate"),
            _req("skill.machine_learning", "intermediate"),
        ],
    ),
    Role(
        id="role.generative_ai_engineer",
        name="Generative AI Engineer",
        description="Builds applications and pipelines on top of generative models.",
        family="ai",
        domains=["Generative AI", "Deep Learning", "Model Deployment"],
        learning_objective_options=_AI_OBJECTIVES,
        required_skills=[
            _req("skill.python", "intermediate"),
            _req("skill.deep_learning", "intermediate"),
            _req("skill.generative_ai", "advanced"),
            _req("skill.model_deployment", "intermediate"),
        ],
    ),
    Role(
        id="role.ai_research_engineer",
        name="AI Research Engineer",
        description="Researches and prototypes new machine learning methods.",
        family="ai",
        domains=["Machine Learning", "Deep Learning", "Statistics"],
        learning_objective_options=_AI_OBJECTIVES,
        required_skills=[
            _req("skill.python", "intermediate"),
            _req("skill.statistics", "advanced"),
            _req("skill.machine_learning", "advanced"),
            _req("skill.deep_learning", "advanced"),
        ],
    ),
    Role(
        id="role.actor",
        name="Actor",
        description="Performs roles across film, television, theatre, and voice.",
        family="performing_arts",
        domains=["Film / Cinema", "Television", "Theatre", "Web Series", "Voice Acting"],
        learning_objective_options=_ACTOR_OBJECTIVES,
        required_skills=[
            _req("skill.acting_techniques", "intermediate"),
            _req("skill.method_acting", "beginner"),
            _req("skill.screen_acting", "beginner"),
            _req("skill.voice_diction", "beginner"),
            _req("skill.body_language", "beginner"),
            _req("skill.improvisation", "beginner"),
            _req("skill.audition_preparation", "beginner"),
        ],
    ),
    Role(
        id="role.software_engineer",
        name="Software Engineer",
        description="Designs and builds software systems and applications.",
        family="software",
        domains=["Backend", "Frontend", "Systems", "Full Stack"],
        required_skills=[
            _req("skill.programming_fundamentals", "intermediate"),
            _req("skill.data_structures", "intermediate"),
            _req("skill.apis", "beginner"),
            _req("skill.testing", "beginner"),
            _req("skill.system_design", "beginner"),
        ],
    ),
    Role(
        id="role.security_analyst",
        name="Security Analyst",
        description="Monitors, detects, and responds to security threats.",
        family="security",
        domains=["Network Security", "Threat Detection", "Incident Response"],
        required_skills=[
            _req("skill.networking_fundamentals", "intermediate"),
            _req("skill.security_fundamentals", "intermediate"),
            _req("skill.threat_detection", "beginner"),
            _req("skill.incident_response", "beginner"),
        ],
    ),
]

# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------
_RESOURCES: list[Resource] = [
    Resource("res.python_crash_course", "Python Crash Course", "course", ["skill.python"],
             "https://docs.python.org/3/tutorial/", "Official Python tutorial.", "beginner", "~1 week", "python.org"),
    Resource("res.statistics_essentials", "Statistics for Data Science", "course", ["skill.statistics"],
             None, "Core statistics: distributions, hypothesis testing, regression.", "beginner", "~1 week", None),
    Resource("res.ml_fundamentals", "Machine Learning Fundamentals", "course", ["skill.machine_learning"],
             None, "Supervised/unsupervised learning, model evaluation.", "intermediate", "~2 weeks", None),
    Resource("res.deep_learning_specialization", "Deep Learning Specialization", "course", ["skill.deep_learning"],
             None, "Neural networks, CNNs, RNNs, training at scale.", "intermediate", "~3 weeks", None),
    Resource("res.generative_ai_primer", "Generative AI Primer", "course", ["skill.generative_ai"],
             None, "Transformers, LLMs, diffusion models, prompting.", "advanced", "~2 weeks", None),
    Resource("res.model_deployment_guide", "Deploying ML Models", "guide", ["skill.model_deployment"],
             None, "Serving models via APIs, containers, and batch jobs.", "intermediate", "~1 week", None),
    Resource("res.mlops_handbook", "MLOps Handbook", "guide", ["skill.mlops"],
             None, "CI/CD for ML, monitoring, and pipeline automation.", "advanced", "~2 weeks", None),
    Resource("res.data_wrangling_guide", "Data Wrangling with Pandas", "guide", ["skill.data_wrangling"],
             None, "Cleaning and reshaping real-world datasets.", "beginner", "~1 week", None),
    Resource("res.data_viz_guide", "Data Visualization Basics", "guide", ["skill.data_visualization"],
             None, "Communicating data with clear, honest charts.", "beginner", "~1 week", None),
    Resource("res.acting_techniques_workshop", "Acting Techniques Workshop", "course", ["skill.acting_techniques"],
             None, "Foundational scene work and character building.", "beginner", "~2 weeks", None),
    Resource("res.method_acting_intro", "Introduction to Method Acting", "course", ["skill.method_acting"],
             None, "Emotional memory and immersive character preparation.", "intermediate", "~2 weeks", None),
    Resource("res.screen_acting_basics", "Screen Acting Basics", "course", ["skill.screen_acting"],
             None, "Acting for camera: framing, continuity, subtlety.", "beginner", "~1 week", None),
    Resource("res.voice_diction_training", "Voice & Diction Training", "course", ["skill.voice_diction"],
             None, "Projection, clarity, and vocal control.", "beginner", "~1 week", None),
    Resource("res.body_language_workshop", "Body Language for Performers", "workshop", ["skill.body_language"],
             None, "Physicality, posture, and non-verbal storytelling.", "beginner", "~1 week", None),
    Resource("res.improv_basics", "Improvisation Basics", "workshop", ["skill.improvisation"],
             None, "Yes-and thinking and staying present on stage.", "beginner", "~1 week", None),
    Resource("res.audition_prep_guide", "Audition Preparation Guide", "guide", ["skill.audition_preparation"],
             None, "Choosing material, cold reads, and callbacks.", "intermediate", "~1 week", None),
    Resource("res.programming_fundamentals_course", "Programming Fundamentals", "course",
             ["skill.programming_fundamentals"], None, "Variables, control flow, functions.", "beginner", "~2 weeks", None),
    Resource("res.dsa_course", "Data Structures & Algorithms", "course", ["skill.data_structures"],
             None, "Arrays, trees, graphs, and complexity analysis.", "intermediate", "~3 weeks", None),
    Resource("res.api_design_guide", "Building APIs", "guide", ["skill.apis"],
             None, "REST fundamentals and API design practices.", "beginner", "~1 week", None),
    Resource("res.system_design_primer", "System Design Primer", "guide", ["skill.system_design"],
             None, "Scaling, caching, and distributed systems basics.", "advanced", "~2 weeks", None),
    Resource("res.testing_guide", "Software Testing Guide", "guide", ["skill.testing"],
             None, "Unit, integration, and end-to-end testing.", "beginner", "~1 week", None),
    Resource("res.networking_fundamentals_course", "Networking Fundamentals", "course",
             ["skill.networking_fundamentals"], None, "TCP/IP, DNS, routing basics.", "beginner", "~1 week", None),
    Resource("res.security_fundamentals_course", "Security Fundamentals", "course", ["skill.security_fundamentals"],
             None, "CIA triad, common attack vectors, defenses.", "beginner", "~2 weeks", None),
    Resource("res.threat_detection_guide", "Threat Detection Guide", "guide", ["skill.threat_detection"],
             None, "Log analysis and detecting anomalous activity.", "intermediate", "~2 weeks", None),
    Resource("res.incident_response_playbook", "Incident Response Playbook", "guide", ["skill.incident_response"],
             None, "Containment, eradication, and recovery steps.", "intermediate", "~1 week", None),
]

# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------
_PROJECTS: list[Project] = [
    Project(
        "proj.house_price_prediction",
        "House Price Prediction",
        "Predict housing prices from tabular data using regression.",
        ["skill.statistics", "skill.machine_learning"],
        ["house", "price", "prediction", "regression", "real estate", "tabular"],
    ),
    Project(
        "proj.image_classifier",
        "Image Classifier",
        "Train a convolutional network to classify images into categories.",
        ["skill.deep_learning"],
        ["image", "vision", "classification", "cnn", "computer vision"],
    ),
    Project(
        "proj.chatbot_assistant",
        "Conversational Assistant",
        "Build an LLM-powered chatbot with retrieval and tool use.",
        ["skill.generative_ai", "skill.python"],
        ["chatbot", "assistant", "llm", "generative", "conversational"],
    ),
    Project(
        "proj.model_deployment_pipeline",
        "Model Deployment Pipeline",
        "Package and serve a trained model with monitoring and CI/CD.",
        ["skill.model_deployment", "skill.mlops"],
        ["deploy", "pipeline", "production", "mlops", "serving"],
    ),
    Project(
        "proj.audition_reel",
        "Short Film Audition Reel",
        "Prepare and film a short scene for a professional audition reel.",
        ["skill.screen_acting", "skill.audition_preparation"],
        ["audition", "reel", "film", "screen", "camera"],
    ),
    Project(
        "proj.stage_monologue",
        "Stage Monologue Performance",
        "Rehearse and perform a monologue with full vocal and physical presence.",
        ["skill.method_acting", "skill.voice_diction", "skill.body_language"],
        ["stage", "theatre", "monologue", "performance", "live"],
    ),
    Project(
        "proj.rest_api_service",
        "REST API Service",
        "Design and build a small production-style REST API.",
        ["skill.apis", "skill.testing"],
        ["api", "backend", "rest", "service"],
    ),
    Project(
        "proj.incident_response_drill",
        "Incident Response Tabletop Drill",
        "Run a simulated security incident from detection to recovery.",
        ["skill.threat_detection", "skill.incident_response"],
        ["incident", "security", "response", "drill", "soc"],
    ),
]


class KnowledgeRepository:
    """Deterministic, in-memory knowledge base. No LLM calls happen here."""

    def __init__(self) -> None:
        self.skills: dict[str, Skill] = {s.id: s for s in _SKILLS}
        self.roles: dict[str, Role] = {r.id: r for r in _ROLES}
        self.resources: list[Resource] = list(_RESOURCES)
        self.projects: list[Project] = list(_PROJECTS)

    def all_roles(self) -> list[Role]:
        return list(self.roles.values())

    def roles_in_family(self, family: str) -> list[Role]:
        return [role for role in self.roles.values() if role.family == family]

    def get_role(self, role_id: str | None) -> Role | None:
        if not role_id:
            return None
        return self.roles.get(role_id)

    def find_role_by_name(self, name: str) -> Role | None:
        if not name:
            return None
        normalized = name.strip().lower()
        for role in self.roles.values():
            if role.name.lower() == normalized:
                return role
        return None

    def get_skill(self, skill_id: str | None) -> Skill | None:
        if not skill_id:
            return None
        return self.skills.get(skill_id)

    def find_skill_by_name(self, name: str) -> Skill | None:
        if not name:
            return None
        normalized = name.strip().lower()
        for skill in self.skills.values():
            if skill.name.lower() == normalized:
                return skill
        return None

    def resources_for_skill(self, skill_id: str) -> list[Resource]:
        return [resource for resource in self.resources if skill_id in resource.skill_ids]

    def project_for_skill(self, skill_id: str) -> Project | None:
        for project in self.projects:
            if skill_id in project.skill_ids:
                return project
        return None

    def match_projects(self, phrases: list[str], role_skill_ids: set[str] | None = None) -> list[Project]:
        """Deterministically rank projects by keyword and skill overlap."""
        blob = " ".join(p.lower() for p in phrases if p)
        role_skill_ids = role_skill_ids or set()
        scored: list[tuple[int, Project]] = []
        for project in self.projects:
            score = 0
            if blob:
                score += sum(1 for keyword in project.keywords if keyword in blob)
            score += len(set(project.skill_ids) & role_skill_ids)
            if score > 0:
                scored.append((score, project))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [project for _, project in scored[:3]]

    def topological_order(self, skill_ids: list[str]) -> list[str]:
        skill_ids_set = set(skill_ids)
        visited: set[str] = set()
        order: list[str] = []

        def visit(sid: str, stack: set[str]) -> None:
            if sid in visited or sid not in skill_ids_set:
                return
            if sid in stack:
                return
            stack.add(sid)
            skill = self.skills.get(sid)
            if skill:
                for prereq in skill.prerequisites:
                    visit(prereq, stack)
            stack.discard(sid)
            visited.add(sid)
            order.append(sid)

        for sid in skill_ids:
            visit(sid, set())
        return order


@lru_cache
def get_repository() -> KnowledgeRepository:
    return KnowledgeRepository()
