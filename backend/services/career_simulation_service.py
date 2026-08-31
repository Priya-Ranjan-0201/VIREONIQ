"""
Career Simulation & Counterfactual Strategic Planning Engine (v9.0.0).
Provides:
  1. Zero-Mutation Counterfactual Scenario Execution
  2. Role Switching & Transferable Skills Proximity Analysis
  3. Skill, Project, and Assessment Investment Projections
  4. Multi-Path Career Comparison Matrix
  5. Time-Budget & Deadline Feasibility Adaptation
  6. Explicit Simulated Evidence Tagging (NOT_VERIFIED / NOT_CREDENTIAL_ELIGIBLE)
  7. Scenario to Active 14-Day Intervention Plan Conversion
"""

from typing import Dict, Any, List, Optional
import uuid
import math
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from db.models import (
    User, Profile, SkillEvidence, CareerSimulation, CareerInterventionPlan, CareerInterventionTask
)
from services.canonical_skill_service import normalize_skill_name
from services.career_readiness_engine import compute_role_career_readiness
from services.role_comparison_service import compute_candidate_role_alignment
from services.career_intervention_engine import generate_career_intervention_plan

logger = logging.getLogger(__name__)

SIMULATION_ENGINE_VERSION = "9.0.0"

ROLE_COMPETENCY_DEFINITIONS = {
    "Backend Engineer": ["Python", "FastAPI", "System Design", "Distributed Systems", "PostgreSQL", "Docker"],
    "Platform Engineer": ["Kubernetes", "Docker", "Cloud", "Terraform", "CI/CD", "Python", "System Design"],
    "Cloud Engineer": ["AWS Cloud", "Docker", "Kubernetes", "Linux", "Terraform", "Networking"],
    "Cybersecurity Engineer": ["Linux", "Networking", "Security Fundamentals", "Threat Detection", "Python", "Cryptography"],
    "AI/ML Engineer": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "MLOps", "Linear Algebra"]
}

ROLE_ADJACENCY_SCORES = {
    ("Backend Engineer", "Platform Engineer"): 91.0,
    ("Backend Engineer", "Cloud Engineer"): 84.0,
    ("Backend Engineer", "Cybersecurity Engineer"): 67.0,
    ("Backend Engineer", "AI/ML Engineer"): 52.0
}

async def run_counterfactual_simulation(
    user_id: uuid.UUID,
    target_role: str,
    simulation_type: str,
    scenario_actions: List[Dict[str, Any]],
    assumptions: Dict[str, Any],
    title: Optional[str] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Executes an isolated counterfactual career scenario without mutating real candidate data.
    """
    # 1. Fetch Candidate Base Twin State
    prof_stmt = select(Profile).where(Profile.user_id == user_id)
    profile = (await db.execute(prof_stmt)).scalars().first() if db else None
    current_role = profile.target_role if profile and profile.target_role else "Backend Engineer"

    skills_stmt = select(SkillEvidence).where(SkillEvidence.user_id == user_id)
    skills = list((await db.execute(skills_stmt)).scalars().all()) if db else []
    skill_map = {normalize_skill_name(s.skill_name): s for s in skills}

    # Baseline readiness
    base_readiness_res = await compute_role_career_readiness(user_id, current_role, db) if db else {}
    base_score = float(base_readiness_res.get("overall_readiness_score", 74.0))

    # 2. Evaluate Role Switch & Transferable Competencies (Section 31 & 32)
    target_role_skills = ROLE_COMPETENCY_DEFINITIONS.get(target_role, ROLE_COMPETENCY_DEFINITIONS["Backend Engineer"])
    transferable_skills = []
    new_gaps = []
    
    for req in target_role_skills:
        norm = normalize_skill_name(req)
        if norm in skill_map:
            s = skill_map[norm]
            transferable_skills.append({
                "skill_name": req,
                "transfer_tier": "HIGH_TRANSFER" if s.evidence_tier in ("VERIFIED", "ASSESSED") else "MEDIUM_TRANSFER",
                "current_tier": s.evidence_tier,
                "current_score": float(s.score or 75.0)
            })
        else:
            new_gaps.append({
                "skill_name": req,
                "status": "CRITICAL_GAP",
                "importance": 90
            })

    # Adjacency Proximity Score
    adj_key = (current_role, target_role)
    adjacency_pct = ROLE_ADJACENCY_SCORES.get(adj_key, 75.0 if current_role == target_role else 60.0)

    # 3. Simulate Hypothetical Actions & Evidence (Section 14 & 15)
    hypothetical_evidence = []
    projected_skill_deltas = {}
    total_delta_sum = 0.0

    for action in scenario_actions:
        skill_name = action.get("skill_name", "System Design")
        action_kind = action.get("action_type", "BUILD_PROJECT")
        sim_score = float(action.get("target_score", 85.0))

        # Explicit Simulated Badge tagging
        sim_item = {
            "skill_name": skill_name,
            "evidence_tier": "SIMULATED",
            "score": sim_score,
            "action_type": action_kind,
            "status": "NOT_VERIFIED",
            "shareable": False,
            "credential_eligible": False,
            "simulated_at": datetime.now(timezone.utc).isoformat()
        }
        hypothetical_evidence.append(sim_item)

        current_val = float(skill_map[normalize_skill_name(skill_name)].score) if normalize_skill_name(skill_name) in skill_map else 50.0
        delta = max(sim_score - current_val, 5.0)
        projected_skill_deltas[skill_name] = {
            "current_score": current_val,
            "projected_score": sim_score,
            "delta": round(delta, 1)
        }
        total_delta_sum += delta

    # 4. Projected Readiness Range & Uncertainty (Section 11, 12, 13)
    # Factor Breakdown: Skill improvement (+5), Evidence strength (+3), Assessment (+2), Uncertainty (+-3)
    skill_factor = min(round(total_delta_sum * 0.15, 1), 8.0)
    evidence_factor = 3.0 if len(hypothetical_evidence) >= 2 else 1.5
    assessment_factor = 2.0 if any(a.get("action_type") == "ASSESSMENT" for a in scenario_actions) else 0.5
    
    total_projected_gain = skill_factor + evidence_factor + assessment_factor
    projected_base = min(round(base_score + total_projected_gain, 1), 94.0)
    projected_min = max(round(projected_base - 3.0, 1), 10.0)
    projected_max = min(round(projected_base + 3.0, 1), 98.0)
    best_case = min(round(projected_base + 4.5, 1), 99.0)
    conservative_case = max(round(projected_base - 4.5, 1), base_score)

    # 5. Time-Aware & Deadline Feasibility (Section 22 & 23)
    daily_time_min = assumptions.get("time_budget_daily_min", 60)
    total_effort_hours = max(len(scenario_actions) * 20, 30)
    estimated_days = math.ceil((total_effort_hours * 60) / max(daily_time_min, 15))
    feasibility = "HIGH" if daily_time_min >= 45 else "TIGHT_SCHEDULE"

    # 6. Sensitivity Analysis (Section 59)
    sensitivity = {
        "critical_driver": scenario_actions[0].get("skill_name", "System Design") if scenario_actions else "General Practice",
        "sensitivity_level": "HIGH",
        "driver_explanation": "Projected readiness depends heavily on achieving target assessment scores in primary gap."
    }

    sim_title = title or f"{current_role} -> {target_role} ({simulation_type})"

    # 7. Record Simulation State
    sim_record = CareerSimulation(
        user_id=user_id,
        title=sim_title,
        target_role=target_role,
        simulation_type=simulation_type,
        base_twin_version="2.0.0",
        assumptions=assumptions,
        hypothetical_evidence=hypothetical_evidence,
        projected_skills=projected_skill_deltas,
        projected_readiness={
            "current_score": base_score,
            "projected_range": [projected_min, projected_max],
            "projected_base": projected_base,
            "best_case": best_case,
            "base_case": projected_base,
            "conservative_case": conservative_case,
            "confidence": "MEDIUM"
        },
        projected_gaps={
            "transferable_skills": transferable_skills,
            "critical_gaps": new_gaps,
            "closed_gaps": [a.get("skill_name") for a in scenario_actions if a.get("target_score", 0) >= 80]
        },
        sensitivity_analysis=sensitivity,
        is_private=True
    )
    if db:
        db.add(sim_record)
        await db.commit()
        await db.refresh(sim_record)

    return {
        "simulation_id": str(sim_record.id),
        "title": sim_record.title,
        "target_role": sim_record.target_role,
        "simulation_type": sim_record.simulation_type,
        "adjacency_proximity_pct": adjacency_pct,
        "projected_readiness": sim_record.projected_readiness,
        "projected_skills": sim_record.projected_skills,
        "projected_gaps": sim_record.projected_gaps,
        "timeline_estimate": {
            "estimated_effort_hours": f"{total_effort_hours - 5} - {total_effort_hours + 10} hours",
            "estimated_duration_days": estimated_days,
            "feasibility": feasibility
        },
        "sensitivity_analysis": sensitivity,
        "hypothetical_evidence": hypothetical_evidence,
        "created_at": sim_record.created_at.isoformat() if sim_record.created_at else None
    }

async def compare_career_paths(
    user_id: uuid.UUID,
    target_roles: List[str],
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Produces multi-path career decision matrix comparing Fit, Effort, Evidence Gap, Upside, and Confidence (Section 6 & 47).
    """
    comparisons = []
    for role in target_roles[:4]:
        sim = await run_counterfactual_simulation(
            user_id=user_id,
            target_role=role,
            simulation_type="ROLE_SWITCH",
            scenario_actions=[{"skill_name": "Core Specialty", "action_type": "ASSESSMENT", "target_score": 85.0}],
            assumptions={"time_budget_daily_min": 60},
            db=db
        )
        comparisons.append({
            "target_role": role,
            "current_fit": "HIGH" if sim["adjacency_proximity_pct"] >= 80 else ("MEDIUM" if sim["adjacency_proximity_pct"] >= 60 else "LOW"),
            "adjacency_score": sim["adjacency_proximity_pct"],
            "current_readiness": sim["projected_readiness"]["current_score"],
            "projected_readiness_range": sim["projected_readiness"]["projected_range"],
            "critical_gaps_count": len(sim["projected_gaps"]["critical_gaps"]),
            "estimated_effort": "Low - Medium" if sim["adjacency_proximity_pct"] >= 80 else "High",
            "strategic_upside": "Very High" if role in ("Cybersecurity Engineer", "AI/ML Engineer", "Platform Engineer") else "High",
            "confidence": "MEDIUM"
        })

    return {
        "compared_roles_count": len(comparisons),
        "comparison_matrix": comparisons,
        "decision_recommendation": {
            "strongest_current_fit": comparisons[0]["target_role"] if comparisons else "Backend Engineer",
            "highest_upside": "Cybersecurity Engineer" if "Cybersecurity Engineer" in target_roles else "AI/ML Engineer"
        }
    }

async def convert_scenario_to_active_plan(
    simulation_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Converts a validated simulation scenario into an active Phase 5 Career Intervention Plan with candidate approval (Section 56).
    """
    sim_stmt = select(CareerSimulation).where(
        and_(CareerSimulation.id == simulation_id, CareerSimulation.user_id == user_id)
    )
    sim = (await db.execute(sim_stmt)).scalars().first()
    if not sim:
        raise ValueError("Simulation scenario not found")

    target_role = sim.target_role
    daily_budget = sim.assumptions.get("time_budget_daily_min", 60)

    # Generate real intervention plan via Phase 5 Engine
    plan_data = await generate_career_intervention_plan(
        user_id=user_id,
        target_role=target_role,
        strategy="BALANCED",
        daily_time_budget_minutes=daily_budget,
        db=db
    )

    return {
        "status": "PLAN_ACTIVATED_FROM_SCENARIO",
        "simulation_id": str(sim.id),
        "intervention_plan_id": plan_data["plan_id"],
        "target_role": target_role,
        "title": plan_data["title"],
        "tasks_count": plan_data["tasks_count"]
    }
