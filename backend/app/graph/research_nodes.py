from __future__ import annotations

import json
import logging
import uuid
from typing import cast

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from app.core.config import get_settings
from app.prompts import render_template
from app.graph.state import LearningState
from app.integrations.llm.openrouter import get_chat_model
from app.schemas.path import LearningStep
from app.schemas.research import (
    CandidatePath,
    LearningResource,
    LearningResourcesOutput,
    RoleResearch,
    SkillRequirement,
    SkillRequirementsOutput,
)
from app.services.learning_path_service import build_dynamic_learning_path
from app.services.research_cache import get_research_cache
from app.services.skill_gap_service import compute_dynamic_skill_gap
from app.services.web_search import get_web_search_service

logger = logging.getLogger(__name__)

def research_role_node(state: LearningState) -> dict:
    target_role = state.get("target_role")
    profile = state.get("learner_profile_json") or {}

    specialization = profile.get("specialization") or state.get("specialization")
    function = profile.get("function") or state.get("function")
    industry = profile.get("industry") or state.get("industry")
    career_intent = profile.get("career_intent") or state.get("career_intent")

    if target_role:
        rich_role = target_role
    elif specialization and function:
        rich_role = f"{specialization} ({function})"
    elif specialization:
        rich_role = specialization
    elif function:
        rich_role = function
    else:
        return {"error": "No target role or function specified for research."}

    cache_key = f"{rich_role}|{industry or ''}"
    logger.info("Starting research: role='%s' industry='%s'", rich_role, industry or "N/A")

    cache = get_research_cache()
    cached = cache.get_role_research(cache_key)
    if cached:
        logger.info("Using cached research for: %s", cache_key)
        return {"role_research": cached.model_dump()}

    search_svc = get_web_search_service()

    query_parts = [rich_role]
    if industry:
        query_parts.append(f"in {industry}")
    query = f"what does a {' '.join(query_parts)} do required skills responsibilities career path"
    results = search_svc.search(query)

    context = "\n\n".join(
        f"Source: {r.url}\nTitle: {r.title}\nContent: {r.content}"
        for r in results
    )

    llm = get_chat_model().with_structured_output(RoleResearch)

    prompt = render_template(
        "role_research.jinja",
        rich_role=rich_role,
        profile=profile,
        search_context=context,
    )
    try:
        research: RoleResearch = llm.invoke([SystemMessage(content=prompt)])
        research.role = rich_role
        from app.schemas.research import Source
        research.sources = [Source(title=r.title, url=r.url) for r in results]
        cache.set_role_research(cache_key, research)
        return {"role_research": research.model_dump()}
    except Exception as exc:
        logger.error("Role research extraction failed: %s", exc)
        return {"error": f"Failed to extract research for {rich_role}"}

def extract_skills_node(state: LearningState) -> dict:
    research_raw = state.get("role_research")
    if not research_raw:
        return {"error": "Missing role_research for skill extraction"}
        
    research = RoleResearch.model_validate(research_raw)
    
    llm = get_chat_model().with_structured_output(SkillRequirementsOutput)
    
    prompt = f"""You are an expert curriculum designer.
Given the following research for a '{research.role}', list the specific skills required.
For each skill, determine its importance (essential, important, optional) and 
the required proficiency level (1=awareness to 5=expert).
Identify prerequisites if any.

Role Research:
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
    target_role = state.get("target_role") or "Target Role"
    learner_skills = state.get("skills") or []
    
    try:
        reqs = [SkillRequirement.model_validate(r) for r in requirements_raw]
        gap_result = compute_dynamic_skill_gap(target_role, reqs, learner_skills)
        return {"skill_gap": gap_result.model_dump()}
    except Exception as exc:
        logger.error("Compute gap failed: %s", exc)
        return {"error": "Failed to compute skill gap"}

def generate_candidate_path_node(state: LearningState) -> dict:
    gap_raw = state.get("skill_gap")
    if not gap_raw:
        return {"error": "Missing skill gap for path generation"}
        
    llm = get_chat_model().with_structured_output(CandidatePath)
    
    prompt = f"""You are an expert learning path creator.
Design a learning path to address the missing and developing skills in this skill gap.
Order the skills logically based on prerequisites.
For each step, explain the reason why it is needed and what the expected outcome is.
Be concise.

Skill Gap:
{json.dumps(gap_raw, indent=2)}
"""
    try:
        candidate: CandidatePath = llm.invoke([SystemMessage(content=prompt)])
        return {"candidate_path": candidate.model_dump()}
    except Exception as exc:
        logger.error("Candidate path generation failed: %s", exc)
        return {"error": "Failed to generate candidate path"}

def research_resources_node(state: LearningState) -> dict:
    candidate_raw = state.get("candidate_path")
    if not candidate_raw:
        return {"error": "Missing candidate path for resource research"}
        
    candidate = CandidatePath.model_validate(candidate_raw)
    search_svc = get_web_search_service()
    llm = get_chat_model().with_structured_output(LearningResourcesOutput)
    
    all_resources: list[LearningResource] = []
    steps_to_research = candidate.steps[:5]
    
    for step in steps_to_research:
        query = f"best courses tutorial learn {step.skill} 2025"
        results = search_svc.search(query, max_results=3)
        
        context = "\n".join(f"- {r.title} ({r.url}): {r.content}" for r in results)
        
        prompt = f"""You are an expert learning resource curator.
Find the best learning resources for the skill '{step.skill}' from these search results.
Extract the title, URL, provider, type, and difficulty.
Only include resources that actually exist in the search results and have URLs.

Search Results:
{context}
"""
        try:
            output: LearningResourcesOutput = llm.invoke([SystemMessage(content=prompt)])
            for res in output.resources:
                res.skills = [step.skill]
                res.reason = f"Highly recommended resource for {step.skill}"
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
