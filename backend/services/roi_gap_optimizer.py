"""
ROI Gap Optimizer Service.
Prioritizes skill gaps using mathematical ROI formula:
  Priority = (Role Importance * Current Gap * Expected Career Impact) / Estimated Effort
Identifies the single highest-leverage intervention for maximum career progression.
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import SkillEvidence, TargetRole
from services.role_intelligence_service import get_role_definition

logger = logging.getLogger(__name__)

EFFORT_MAP = {
    "LOW": 1.0,      # ~3-5 days
    "MEDIUM": 2.0,   # ~7-14 days
    "HIGH": 3.5      # ~21-30 days
}

SKILL_DIFFICULTY_EFFORT = {
    "System Design": "MEDIUM",
    "Data Structures": "MEDIUM",
    "PostgreSQL": "LOW",
    "Redis": "LOW",
    "Docker": "LOW",
    "Kubernetes": "HIGH",
    "REST APIs": "LOW",
    "FastAPI": "LOW",
    "React": "LOW",
    "TypeScript": "LOW",
    "Distributed Systems": "HIGH",
    "Machine Learning": "HIGH",
    "Cloud Security": "MEDIUM"
}

async def calculate_roi_gaps(
    user_id: uuid.UUID,
    target_role_name: str,
    db: AsyncSession
) -> List[Dict[str, Any]]:
    """
    Computes ROI priority score for each missing or underdeveloped competency.
    """
    # 1. Fetch candidate skills
    stmt = select(SkillEvidence).where(SkillEvidence.user_id == user_id)
    skills = list((await db.execute(stmt)).scalars().all())
    skill_map = {s.skill_name.lower(): s for s in skills}

    # 2. Fetch role requirements
    role_def = get_role_definition(target_role_name)
    required_skills = role_def.get("required_skills", [])

    gaps = []
    for req in required_skills:
        skill_name = req["name"]
        skill_lower = skill_name.lower()
        importance = float(req.get("importance", 0.8)) * 100.0 # 0-100 scale
        min_prof = float(req.get("min_proficiency", 70.0))

        current_score = 0.0
        current_tier = "NONE"
        if skill_lower in skill_map:
            cand_skill = skill_map[skill_lower]
            current_score = float(cand_skill.score or 0.0)
            current_tier = cand_skill.evidence_tier

        gap_value = max(0.0, min_prof - current_score)
        if current_score == 0.0:
            gap_value = min_prof # Full gap

        # Only consider meaningful gaps
        if gap_value > 5.0 or current_tier in ("NONE", "CLAIMED"):
            effort_str = SKILL_DIFFICULTY_EFFORT.get(skill_name, "MEDIUM")
            effort_numeric = EFFORT_MAP.get(effort_str, 2.0)
            
            # Expected impact (0-100 scale based on importance and gap)
            career_impact = min(100.0, (importance * 0.6) + (gap_value * 0.4))
            
            # Priority = (Importance * Gap * Career Impact) / (Effort * 100)
            priority_score = round((importance * gap_value * (career_impact / 100.0)) / effort_numeric, 1)

            # Prescriptive project recommendation
            project_rec = _recommend_project_for_skill(skill_name)

            gaps.append({
                "skill_name": skill_name,
                "role_importance": round(importance, 1),
                "current_score": round(current_score, 1),
                "current_tier": current_tier,
                "gap_magnitude": round(gap_value, 1),
                "estimated_effort": effort_str,
                "expected_career_impact": "VERY HIGH" if career_impact > 80 else ("HIGH" if career_impact > 60 else "MEDIUM"),
                "priority_score": priority_score,
                "recommended_action": project_rec["action"],
                "recommended_project": project_rec["project"],
                "projected_cri_boost": round(min(5.5, (priority_score / 350.0)), 1)
            })

    # Sort by highest ROI priority
    gaps.sort(key=lambda x: x["priority_score"], reverse=True)
    return gaps

def _recommend_project_for_skill(skill_name: str) -> Dict[str, str]:
    recommendations = {
        "System Design": {
            "action": "Build a distributed URL shortener with rate limiting and Redis caching.",
            "project": "Distributed URL Shortener"
        },
        "Redis": {
            "action": "Implement a distributed sliding-window rate limiter middleware with Redis.",
            "project": "Redis Rate Limiter & Cache Layer"
        },
        "PostgreSQL": {
            "action": "Design normalized schema with composite indexing and explain analyze query tuning.",
            "project": "High-Throughput Financial Ledger DB"
        },
        "FastAPI": {
            "action": "Develop asynchronous REST API with Pydantic v2 schemas and JWT auth.",
            "project": "Production Async Microservice"
        },
        "Docker": {
            "action": "Multi-stage Dockerfile build with non-root user and minimal scratch base image.",
            "project": "Hardened Container Deployment"
        },
        "Data Structures": {
            "action": "Solve 10 medium algorithmic problems focused on two pointers and binary search trees.",
            "project": "Algorithmic Sandbox Mastery"
        },
        "Kubernetes": {
            "action": "Deploy microservices on Minikube with Horizontal Pod Autoscaler and Ingress Controller.",
            "project": "Kubernetes Cluster Deployment"
        }
    }
    return recommendations.get(skill_name, {
        "action": f"Build an end-to-end practical implementation demonstrating production {skill_name}.",
        "project": f"{skill_name} Production Project"
    })
