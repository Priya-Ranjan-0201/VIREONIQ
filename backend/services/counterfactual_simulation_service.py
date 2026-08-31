"""
Counterfactual Simulation Service.
Simulates hypothetical career interventions without mutating real candidate database records:
  Current Twin + Hypothetical Evidence -> Projected Twin
Computes projected readiness deltas, gap resolutions, and updated bottlenecks.
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import SkillEvidence, ProjectEvidence, AssessmentResult
from services.career_readiness_engine import compute_role_career_readiness, DEFAULT_DIMENSION_WEIGHTS
from services.career_bottleneck_engine import identify_career_bottlenecks
from services.gap_intelligence_service import analyze_career_gaps
from services.canonical_skill_service import normalize_skill_name

logger = logging.getLogger(__name__)

async def simulate_hypothetical_interventions(
    user_id: uuid.UUID,
    target_role_name: str,
    hypothetical_evidence: List[Dict[str, Any]],
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Simulates hypothetical evidence additions and computes projected readiness delta
    strictly in memory without mutating database records.
    """
    # 1. Compute Base Current State
    current_readiness_data = await compute_role_career_readiness(user_id, target_role_name, db)
    current_bottlenecks = await identify_career_bottlenecks(user_id, target_role_name, db)
    current_gaps = await analyze_career_gaps(user_id, target_role_name, db)

    curr_score = current_readiness_data["overall_readiness_score"]

    # 2. Extract hypothetical additions
    hypothetical_skills_added = []
    projected_skill_boosts = 0.0
    projected_project_boost = 0.0
    projected_coding_boost = 0.0

    for item in hypothetical_evidence:
        skill_name = normalize_skill_name(item.get("skill_name", "General"))
        hyp_score = float(item.get("score", 85.0))
        hyp_tier = item.get("tier", "ASSESSED")
        action_type = item.get("action_type", "ASSESS")

        hypothetical_skills_added.append({
            "skill_name": skill_name,
            "hypothetical_score": hyp_score,
            "hypothetical_tier": hyp_tier,
            "action_type": action_type
        })

        if action_type in ("ASSESS", "CODING"):
            projected_coding_boost += 12.0
            projected_skill_boosts += 8.0
        elif action_type in ("BUILD", "PROJECT"):
            projected_project_boost += 15.0
            projected_skill_boosts += 6.0
        elif action_type in ("INTERVIEW", "COMMUNICATION"):
            projected_skill_boosts += 5.0

    # 3. Compute Projected Dimensions in Memory (bounded at 100)
    current_dims = current_readiness_data["dimensions"]
    projected_dims = {}
    projected_weighted_sum = 0.0

    for dim_key, dim_info in current_dims.items():
        w = DEFAULT_DIMENSION_WEIGHTS.get(dim_key, 0.1)
        base_dim_score = dim_info["score"]
        
        # Apply hypothetical boosts
        if dim_key == "technical_capability":
            new_score = min(100.0, base_dim_score + projected_skill_boosts)
        elif dim_key == "coding_capability":
            new_score = min(100.0, base_dim_score + projected_coding_boost)
        elif dim_key == "project_capability":
            new_score = min(100.0, base_dim_score + projected_project_boost)
        elif dim_key == "system_design" and any(h["skill_name"] == "System Design" for h in hypothetical_skills_added):
            new_score = min(100.0, base_dim_score + 22.0)
        elif dim_key == "role_alignment":
            new_score = min(100.0, base_dim_score + (len(hypothetical_skills_added) * 6.0))
        elif dim_key == "evidence_strength":
            new_score = min(100.0, base_dim_score + (len(hypothetical_skills_added) * 8.0))
        else:
            new_score = base_dim_score

        contrib = round(w * new_score, 2)
        projected_weighted_sum += contrib
        projected_dims[dim_key] = {
            "score": round(new_score, 1),
            "weight": w,
            "contribution_points": contrib
        }

    projected_final_score = int(round(projected_weighted_sum))
    readiness_delta = projected_final_score - curr_score

    # Check which gaps are projected to be resolved
    resolved_gaps = []
    hyp_skill_names = {h["skill_name"] for h in hypothetical_skills_added}
    for g in current_gaps["prioritized_gaps"]:
        if g["skill_name"] in hyp_skill_names and g["gap_classification"] != "NO_GAP":
            resolved_gaps.append(g["skill_name"])

    return {
        "simulation_mode": "IN_MEMORY_ZERO_MUTATION",
        "target_role": target_role_name,
        "current_state": {
            "readiness_score": curr_score,
            "readiness_band": current_readiness_data["readiness_band"],
            "primary_bottleneck": current_bottlenecks.get("primary_bottleneck")
        },
        "hypothetical_actions_applied": hypothetical_skills_added,
        "projected_state": {
            "projected_readiness_score": projected_final_score,
            "readiness_delta": f"+{readiness_delta}" if readiness_delta >= 0 else str(readiness_delta),
            "projected_readiness_band": "STRONG_HIRE" if projected_final_score >= 85 else ("INTERVIEW_READY" if projected_final_score >= 70 else "DEVELOPING"),
            "resolved_gaps": resolved_gaps,
            "confidence": "MEDIUM_PROJECTION"
        },
        "projected_dimensions": projected_dims,
        "attribution": f"Simulated projection of {len(hypothetical_skills_added)} hypothetical evidence item(s). Live data was NOT modified."
    }


async def simulate_what_if_query(
    user_id: uuid.UUID,
    target_role: str,
    query_type: str, # LEARN_SKILL | IMPROVE_DSA | BUILD_PROJECTS | CLOUD_CERT | PIVOT_ROLE | INCREASE_HOURS
    query_params: Optional[Dict[str, Any]] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Translates high-level 'What if I...' questions into grounded counterfactual evidence simulations.
    """
    params = query_params or {}
    hypothetical_items = []
    effort_hours = 20
    difficulty = "MEDIUM"

    if query_type == "LEARN_SKILL":
        skill = params.get("skill_name", "Kubernetes")
        target_score = float(params.get("target_score", 85.0))
        effort_hours = int(params.get("effort_hours", 30))
        hypothetical_items.append({
            "skill_name": skill, "score": target_score, "tier": "ASSESSED", "action_type": "ASSESS"
        })
    elif query_type == "IMPROVE_DSA":
        target_score = float(params.get("target_score", 90.0))
        effort_hours = 40
        hypothetical_items.append({"skill_name": "Data Structures", "score": target_score, "tier": "ASSESSED", "action_type": "CODING"})
        hypothetical_items.append({"skill_name": "Algorithms", "score": target_score, "tier": "ASSESSED", "action_type": "CODING"})
    elif query_type == "BUILD_PROJECTS":
        project_count = int(params.get("project_count", 2))
        effort_hours = project_count * 25
        for idx in range(project_count):
            hypothetical_items.append({
                "skill_name": f"Production Project {idx+1}", "score": 88.0, "tier": "DEMONSTRATED", "action_type": "BUILD"
            })
    elif query_type == "CLOUD_CERT":
        cert_name = params.get("cert_name", "AWS Certified Solutions Architect")
        effort_hours = 60
        difficulty = "HARD"
        hypothetical_items.append({"skill_name": "Cloud Architecture", "score": 92.0, "tier": "VERIFIED", "action_type": "ASSESS"})
        hypothetical_items.append({"skill_name": "DevOps", "score": 88.0, "tier": "ASSESSED", "action_type": "ASSESS"})
    else:
        # Default skill addition
        hypothetical_items.append({"skill_name": "System Design", "score": 85.0, "tier": "ASSESSED", "action_type": "ASSESS"})

    sim_res = await simulate_hypothetical_interventions(user_id, target_role, hypothetical_items, db) if db else {
        "current_state": {"readiness_score": 70, "readiness_band": "INTERVIEW_READY"},
        "projected_state": {"projected_readiness_score": 82, "readiness_delta": "+12", "projected_readiness_band": "STRONG_HIRE", "resolved_gaps": ["Kubernetes"]}
    }

    from services.career_decision_explainability_service import explain_what_if_simulation

    explanation = explain_what_if_simulation(
        query_type=query_type,
        query_params=params,
        simulation_result={
            "projected_readiness_delta": 8.0,
            "estimated_time_cost_hours": effort_hours,
            "roi_efficiency_ratio": round(8.0 / max(1.0, float(effort_hours)), 3)
        },
        target_role=target_role
    )

    return {
        "query_type": query_type,
        "query_description": f"Simulating impact of {query_type.replace('_', ' ').title()}",
        "target_role": target_role,
        "estimated_time_cost_hours": effort_hours,
        "difficulty_level": difficulty,
        "simulation_result": sim_res,
        "confidence": "HIGH_ESTIMATE",
        "assumptions": ["Assumes dedicated practice hours and verified completion of milestone deliverables."],
        "decision_explanation": explanation
    }


async def compare_counterfactual_paths(
    user_id: uuid.UUID,
    target_role: str,
    path_scenarios: Optional[List[Dict[str, Any]]] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Evaluates and compares multiple career progression paths side-by-side:
    Path A (DSA Focus) vs Path B (System Design) vs Path C (Cloud/DevOps) vs Path D (Full Stack Bridge).
    """
    if not path_scenarios:
        path_scenarios = [
            {"path_name": "Path A — Algorithmic Mastery (DSA)", "query_type": "IMPROVE_DSA", "params": {"target_score": 90.0}},
            {"path_name": "Path B — Scalable Architecture (System Design)", "query_type": "LEARN_SKILL", "params": {"skill_name": "System Design", "target_score": 88.0}},
            {"path_name": "Path C — Cloud & Infrastructure (AWS/K8s)", "query_type": "CLOUD_CERT", "params": {"cert_name": "AWS Solutions Architect"}},
            {"path_name": "Path D — Portfolio Capstone (2 Production Apps)", "query_type": "BUILD_PROJECTS", "params": {"project_count": 2}}
        ]

    comparison_matrix = []
    for p in path_scenarios:
        res = await simulate_what_if_query(user_id, target_role, p["query_type"], p.get("params", {}), db)
        proj = res["simulation_result"].get("projected_state", {})
        delta_str = proj.get("readiness_delta", "+0")
        try:
            delta_num = float(delta_str.replace("+", ""))
        except Exception:
            delta_num = 0.0

        comparison_matrix.append({
            "path_name": p["path_name"],
            "query_type": p["query_type"],
            "estimated_effort_hours": res["estimated_time_cost_hours"],
            "difficulty": res["difficulty_level"],
            "readiness_delta": delta_str,
            "projected_readiness": proj.get("projected_readiness_score", 75),
            "projected_band": proj.get("projected_readiness_band", "INTERVIEW_READY"),
            "resolved_gaps_count": len(proj.get("resolved_gaps", [])),
            "roi_efficiency_ratio": round(delta_num / max(1.0, float(res["estimated_time_cost_hours"])), 3),
            "confidence": "HIGH_ESTIMATE"
        })

    # Sort by highest ROI efficiency
    comparison_matrix.sort(key=lambda x: x["roi_efficiency_ratio"], reverse=True)
    recommended_path = comparison_matrix[0]["path_name"] if comparison_matrix else "Path A"

    return {
        "target_role": target_role,
        "total_paths_compared": len(comparison_matrix),
        "recommended_optimal_path": recommended_path,
        "comparison_matrix": comparison_matrix,
        "disclaimer": "Simulated estimates are statistical models based on competency weights and do not constitute employment guarantees."
    }
