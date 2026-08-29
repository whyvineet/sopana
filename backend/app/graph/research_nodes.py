from __future__ import annotations

import json
import logging
import uuid
from typing import cast

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.prompts import render_template
from app.graph.state import LearningState
from app.integrations.llm.openrouter import get_chat_model
from app.schemas.path import LearningStep
from app.schemas.research import (
    CandidatePath,
    LearningResource,
    LearningResourcesOutput,
    GoalResearch,
    SkillRequirement,
    SkillRequirementsOutput,
)
from app.services.learning_path_service import build_dynamic_learning_path
from app.services.research_cache import get_research_cache
from app.services.skill_gap_service import compute_dynamic_skill_gap
from app.services.web_search import get_web_search_service

logger = logging.getLogger(__name__)

class SearchQueries(BaseModel):
    queries: list[str] = Field(description="List of search queries to execute")

def research_goal_node(state: LearningState) -> dict:
    target_role = state.get("target_role")
    goal = state.get("goal")
    goal_type = state.get("goal_type") or "unresolved"
    
    if not goal and not target_role:
        return {"error": "No goal or target role specified for research."}
        
    topic = target_role if goal_type == "career" and target_role else goal
    cache_key = f"{topic}|{goal_type}"
    logger.info("Starting research: topic='%s' type='%s'", topic, goal_type)

    cache = get_research_cache()
    cached = cache.get_role_research(cache_key)
    if cached:
        logger.info("Using cached research for: %s", cache_key)
        return {"goal_research": cached.model_dump()}

    search_svc = get_web_search_service()
    
    # 1. Generate dynamic search queries
    query_llm = get_chat_model().with_structured_output(SearchQueries)
    query_prompt = f"""You are an expert curriculum researcher. 
The learner has the following goal: '{topic}'
Goal Type: {goal_type}
Experience Level: {state.get("experience_level", "unknown")}

Generate 2-3 highly specific web search queries to understand what is required to achieve this goal.
- For a 'career', search for role responsibilities, required skills, and industry requirements.
- For 'academic', search for typical syllabus, core concepts, and prerequisites.
- For 'skill', search for fundamentals, progression, and practical applications.
- For 'hobby', search for beginner guides, progressive practice, and fundamentals.
"""
    try:
        query_out: SearchQueries = query_llm.invoke([SystemMessage(content=query_prompt)])
        queries = query_out.queries[:3]
    except Exception as exc:
        logger.warning("Failed to generate dynamic queries, falling back: %s", exc)
        queries = [f"what is required to learn {topic}"]

    # 2. Execute searches
    results = []
    for q in queries:
        results.extend(search_svc.search(q, max_results=3))
        
    # Deduplicate results by URL
    seen_urls = set()
    unique_results = []
    for r in results:
        if r.url not in seen_urls:
            unique_results.append(r)
            seen_urls.add(r.url)

    context = "\n\n".join(
        f"Source: {r.url}\nTitle: {r.title}\nContent: {r.content}"
        for r in unique_results[:6]
    )

    # 3. Extract GoalResearch
    llm = get_chat_model().with_structured_output(GoalResearch)
    prompt = f"""You are an expert learning researcher.
Synthesize the search results into a comprehensive research document for the goal: '{topic}' (Type: {goal_type}).
Extract the core topics, optional topics, practical applications, and tools/methods.

Search Results:
{context}
"""
    try:
        research: GoalResearch = llm.invoke([SystemMessage(content=prompt)])
        research.goal = topic
        from app.schemas.research import Source
        research.sources = [Source(title=r.title, url=r.url) for r in unique_results[:6]]
        cache.set_role_research(cache_key, research)
        return {"goal_research": research.model_dump()}
    except Exception as exc:
        logger.error("Goal research extraction failed: %s", exc)
        return {"error": f"Failed to extract research for {topic}"}


def extract_skills_node(state: LearningState) -> dict:
    research_raw = state.get("goal_research")
    goal_type = state.get("goal_type") or "unresolved"
    
    if not research_raw:
        return {"error": "Missing goal_research for skill extraction"}
        
    research = GoalResearch.model_validate(research_raw)
    
    llm = get_chat_model().with_structured_output(SkillRequirementsOutput)
    
    term = "academic concepts" if goal_type == "academic" else "skills"
    
    prompt = f"""You are an expert curriculum designer.
Given the following research for '{research.goal}', list the specific {term} required to master it.
For each item, determine its importance (essential, important, optional) and 
the required proficiency level (1=awareness to 5=expert).
Identify prerequisites if any.

Goal Research:
{json.dumps(research_raw, indent=2)}
"""
    try:
        output: SkillRequirementsOutput = llm.invoke([SystemMessage(content=prompt)])
        reqs = [req.model_dump() for req in output.skill_requirements]
        return {"skill_requirements": reqs}
    except Exception as exc:
        logger.error("Skill extraction failed: %s", exc)
        return {"error": "Failed to extract skill requirements"}


def compute_gap_node(state: LearningState) -> dict:
    requirements_raw = state.get("skill_requirements") or []
    target_role = state.get("target_role")
    goal = state.get("goal")
    goal_type = state.get("goal_type") or "unresolved"
    
    topic = target_role if goal_type == "career" and target_role else (goal or "Unknown Goal")
    learner_skills = state.get("skills") or []
    
    try:
        reqs = [SkillRequirement.model_validate(r) for r in requirements_raw]
        gap_result = compute_dynamic_skill_gap(topic, reqs, learner_skills)
        return {"skill_gap": gap_result.model_dump()}
    except Exception as exc:
        logger.error("Compute gap failed: %s", exc)
        return {"error": "Failed to compute skill gap"}


def generate_candidate_path_node(state: LearningState) -> dict:
    gap_raw = state.get("skill_gap")
    if not gap_raw:
        return {"error": "Missing skill gap for path generation"}
        
    llm = get_chat_model().with_structured_output(CandidatePath)
    
    preferences = {
        "interests": state.get("interests", []),
        "learning_objectives": state.get("learning_objectives", []),
        "experience_level": state.get("experience_level", "none"),
        "goal_type": state.get("goal_type", "unresolved")
    }
    
    prompt = f"""You are an expert learning path creator.
Design a highly personalized learning path to address the missing and developing skills/concepts in this gap.

Learner Profile & Preferences:
{json.dumps(preferences, indent=2)}

CRITICAL INSTRUCTIONS:
1. The learner's preferences MUST influence the learning order, resource types, activity types, practice frequency, and milestones.
2. Order the skills logically based on prerequisites and preferences.
3. For each step, explain the reason why it is needed and what the expected outcome is.
4. If appropriate for the goal_type and objectives (e.g., practice sets for academic, coding projects for software), generate a practical 'project' for the step to apply the skill. 

Skill Gap:
{json.dumps(gap_raw, indent=2)}
"""
    try:
        candidate: CandidatePath = llm.invoke([SystemMessage(content=prompt)])
        return {"candidate_path": candidate.model_dump()}
    except Exception as exc:
        logger.error("Candidate path generation failed: %s", exc)
        return {"error": "Failed to generate candidate path"}


class ValidationResult(BaseModel):
    is_valid: bool
    reason: str

def validate_path_node(state: LearningState) -> dict:
    candidate_raw = state.get("candidate_path")
    if not candidate_raw:
        return {"error": "Missing candidate path for validation"}
        
    llm = get_chat_model().with_structured_output(ValidationResult)
    
    profile = {
        "goal": state.get("goal"),
        "target_role": state.get("target_role"),
        "goal_type": state.get("goal_type"),
        "interests": state.get("interests"),
        "objectives": state.get("learning_objectives")
    }
    
    prompt = f"""You are a quality assurance evaluator.
Check if the following learning path genuinely matches the learner's profile and goal type.
If the path seems to be hallucinated or teaching an unrelated topic (e.g. teaching Python for a Linear Algebra exam when no programming was requested), reject it.

Learner Profile:
{json.dumps(profile, indent=2)}

Candidate Path:
{json.dumps(candidate_raw, indent=2)}
"""
    try:
        result: ValidationResult = llm.invoke([SystemMessage(content=prompt)])
        if not result.is_valid:
            logger.warning("Path validation failed: %s", result.reason)
            return {"error": f"Path validation failed: {result.reason}"}
        return {}
    except Exception as exc:
        logger.error("Validation failed: %s", exc)
        # Proceed if validation crashes to avoid bricking
        return {}


def research_resources_node(state: LearningState) -> dict:
    candidate_raw = state.get("candidate_path")
    if not candidate_raw:
        return {"error": "Missing candidate path for resource research"}
        
    candidate = CandidatePath.model_validate(candidate_raw)
    search_svc = get_web_search_service()
    llm = get_chat_model().with_structured_output(LearningResourcesOutput)
    query_llm = get_chat_model().with_structured_output(SearchQueries)
    
    interests = state.get("interests", [])
    interests_str = ", ".join(interests) if interests else "standard tutorials"
    
    all_resources: list[LearningResource] = []
    steps_to_research = candidate.steps[:5]
    
    for step in steps_to_research:
        query_prompt = f"""Generate 1 precise web search query to find the best learning resources for '{step.skill}'.
The learner prefers: {interests_str}
Goal type: {state.get("goal_type", "unknown")}
Return exactly 1 highly targeted query."""
        try:
            q_out = query_llm.invoke([SystemMessage(content=query_prompt)])
            query = q_out.queries[0] if q_out.queries else f"best ways to learn {step.skill} {interests_str}"
        except Exception:
            query = f"best ways to learn {step.skill} {interests_str}"
            
        results = search_svc.search(query, max_results=3)
        
        context = "\n".join(f"- {r.title} ({r.url}): {r.content}" for r in results)
        
        prompt = f"""You are an expert learning resource curator.
Find the best learning resources for the skill/concept '{step.skill}' from these search results.
The learner prefers: {interests_str}. Select resources that best match these preferences.
Extract the title, URL, provider, type, and difficulty.
Only include resources that actually exist in the search results and have URLs.

Search Results:
{context}
"""
        try:
            output: LearningResourcesOutput = llm.invoke([SystemMessage(content=prompt)])
            for res in output.resources:
                res.skills = [step.skill]
                res.reason = f"Matches preferences ({interests_str}) for {step.skill}"
                res.is_verified = True
                all_resources.append(res)
        except Exception as exc:
            logger.warning("Resource extraction failed for %s: %s", step.skill, exc)
    
    found_skills = {res.skills[0] for res in all_resources if res.skills}
    for step in candidate.steps:
        if step.skill not in found_skills:
            all_resources.append(
                LearningResource(
                    title=f"Fundamentals of {step.skill}",
                    url=None,
                    provider="Pending Resources",
                    type="other",
                    skills=[step.skill],
                    difficulty="beginner",
                    estimated_duration=step.estimated_duration,
                    reason=f"No verified resources found yet. {step.reason}",
                    is_verified=False
                )
            )

    return {"researched_resources": [r.model_dump() for r in all_resources]}


def finalize_path_node(state: LearningState) -> dict:
    try:
        gap_raw = state.get("skill_gap")
        candidate_raw = state.get("candidate_path")
        resources_raw = state.get("researched_resources") or []
        
        from app.schemas.path import SkillGapResult
        
        gap = SkillGapResult.model_validate(gap_raw)
        candidate = CandidatePath.model_validate(candidate_raw)
        resources = [LearningResource.model_validate(r) for r in resources_raw]
        
        final_path = build_dynamic_learning_path(gap, candidate, resources)
        
        return {
            "learning_path": final_path.model_dump(),
            "research_status": "complete",
            "current_stage": "complete",
        }
    except Exception as exc:
        logger.error("Finalize path failed: %s", exc)
        return {"error": "Failed to build final learning path"}
