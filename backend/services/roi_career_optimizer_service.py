"""
ROI Career Optimizer & Next Best Career Action Service.
Ranks candidate career actions by mathematical ROI:
  ROI = (Expected Career Impact * Role Importance * Gap Reduction * Evidence Value) / (Effort Hours * Difficulty Factor)
Features:
  - Multi-Gap Closure Detection (e.g. 1 project closing 3+ gaps)
  - Prerequisite-Aware Gap Dependency Ordering
  - Transparent Intervention Previews (Current Readiness -> Projected Readiness Delta)
  - User Control (Accept, Reject with reason, Postpone)
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import SkillEvidence, ProjectEvidence, AssessmentResult, User
from services.gap_intelligence_service import analyze_career_gaps
from services.career_readiness_engine import compute_role_career_readiness
from services.canonical_skill_service import normalize_skill_name

logger = logging.getLogger(__name__)

# Curated High-Leverage Interventions Catalog with Multi-Gap Closure Capabilities
CURATED_INTERVENTIONS = [
    {
        "id": "action-dist-sys-proj",
        "title": "Build Distributed Notification & Task Processing Engine",
        "action_type": "BUILD",
        "target_skills": ["System Design", "Distributed Systems", "Redis", "FastAPI", "Testing"],
        "primary_gap": "System Design",
        "estimated_hours_min": 12,
        "estimated_hours_max": 18,
        "difficulty_factor": 1.4,
        "evidence_value": 0.90, # Generates DEMONSTRATED repository evidence
        "description": "Architect an asynchronous worker queue with Redis and FastAPI, implementing idempotency and rate limiting.",
        "deliverable_type": "GITHUB_REPOSITORY"
    },
    {
        "id": "action-dsa-sandbox",
        "title": "Complete Graph & Dynamic Programming Sandbox Mastery",
        "action_type": "ASSESS",
        "target_skills": ["Data Structures", "Algorithms", "Python"],
        "primary_gap": "Data Structures",
        "estimated_hours_min": 6,
        "estimated_hours_max": 10,
        "difficulty_factor": 1.2,
        "evidence_value": 0.95, # Generates ASSESSED controlled evidence
        "description": "Solve 8 algorithmic challenges with verified O(N) AST runtime complexity and automated test suites.",
        "deliverable_type": "SANDBOX_ASSESSMENT"
    },
    {
        "id": "action-postgres-optimization",
        "title": "Database Indexing & Query Execution Optimization Project",
        "action_type": "BUILD",
        "target_skills": ["PostgreSQL", "SQL", "System Design"],
        "primary_gap": "PostgreSQL",
        "estimated_hours_min": 8,
        "estimated_hours_max": 14,
        "difficulty_factor": 1.1,
        "evidence_value": 0.85,
        "description": "Benchmark complex SQL joins, implement composite B-Tree indexes, and produce EXPLAIN ANALYZE performance reports.",
        "deliverable_type": "GITHUB_REPOSITORY"
    },
    {
        "id": "action-sysdesign-interview",
        "title": "AI Adaptive System Architecture Mock Interview",
        "action_type": "INTERVIEW",
        "target_skills": ["System Design", "Communication", "Interview Readiness"],
        "primary_gap": "System Design",
        "estimated_hours_min": 2,
        "estimated_hours_max": 4,
        "difficulty_factor": 1.3,
        "evidence_value": 0.88,
        "description": "Design a high-concurrency URL shortener with distributed caching, partition strategy, and back-of-the-envelope estimation.",
        "deliverable_type": "INTERVIEW_RUBRIC"
    },
    {
        "id": "action-docker-k8s-deploy",
        "title": "Containerize & Deploy Microservice on Kubernetes",
        "action_type": "BUILD",
        "target_skills": ["Docker", "Kubernetes", "DevOps"],
        "primary_gap": "Kubernetes",
        "estimated_hours_min": 10,
        "estimated_hours_max": 16,
        "difficulty_factor": 1.5,
        "evidence_value": 0.85,
        "description": "Write multi-stage Dockerfiles, Helm charts, and configure Horizontal Pod Autoscalers with health probes.",
        "deliverable_type": "DEPLOYED_SERVICE"
    }
]

# Prerequisite Rules (skill -> required prerequisites)
PREREQUISITES_MAP = {
    "Distributed Systems": ["Data Structures", "Python", "REST APIs"],
    "System Design": ["Data Structures", "PostgreSQL"],
    "Kubernetes": ["Docker"]
}

async def compute_next_best_career_actions(
    user_id: uuid.UUID,
    target_role_name: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Evaluates candidate gaps against actionable interventions to compute prioritized Next Best Actions.
    """
    # 1. Fetch Current Readiness & Gaps
    readiness_data = await compute_role_career_readiness(user_id, target_role_name, db)
    current_readiness = readiness_data["overall_readiness_score"]

    gap_data = await analyze_career_gaps(user_id, target_role_name, db)
    gaps = gap_data["prioritized_gaps"]
    gap_by_skill = {normalize_skill_name(g["skill_name"]): g for g in gaps}

    # Fetch candidate skills to check prerequisites
    stmt = select(SkillEvidence).where(SkillEvidence.user_id == user_id)
    skills = list((await db.execute(stmt)).scalars().all())
    cand_skill_map = {normalize_skill_name(s.skill_name): s for s in skills}

    ranked_actions = []

    for intervention in CURATED_INTERVENTIONS:
        # Check if intervention targets candidate's active gaps
        addressed_gaps = []
        total_importance_addressed = 0.0
        total_magnitude_addressed = 0.0

        for s_name in intervention["target_skills"]:
            norm_name = normalize_skill_name(s_name)
            if norm_name in gap_by_skill:
                g = gap_by_skill[norm_name]
                if g["gap_classification"] in ("CRITICAL_GAP", "MAJOR_GAP", "MODERATE_GAP", "MINOR_GAP", "UNKNOWN"):
                    addressed_gaps.append({
                        "skill_name": norm_name,
                        "classification": g["gap_classification"],
                        "importance": g["role_importance"]
                    })
                    total_importance_addressed += g["role_importance"]
                    total_magnitude_addressed += (g["gap_magnitude"] if g["gap_magnitude"] is not None else 2.0)

        # Only consider action if it closes at least 1 gap
        if not addressed_gaps:
            continue

        # Prerequisite check
        prereqs = PREREQUISITES_MAP.get(intervention["primary_gap"], [])
        unmet_prereqs = []
        for p in prereqs:
            p_norm = normalize_skill_name(p)
            if p_norm not in cand_skill_map or cand_skill_map[p_norm].evidence_tier in ("CLAIMED", "NONE"):
                unmet_prereqs.append(p_norm)

        # Multi-Gap Closure Factor (bonus for closing 3+ gaps simultaneously)
        multi_gap_bonus = 1.0 + (0.15 * max(0, len(addressed_gaps) - 1))

        # ROI Formula:
        # (Average Importance * Total Magnitude * Evidence Value * Multi Gap Bonus) / (Effort Hours * Difficulty)
        avg_effort = (intervention["estimated_hours_min"] + intervention["estimated_hours_max"]) / 2.0
        difficulty = intervention["difficulty_factor"]
        ev_val = intervention["evidence_value"]
        
        raw_roi = ((total_importance_addressed / len(addressed_gaps)) * total_magnitude_addressed * ev_val * multi_gap_bonus) / (avg_effort * difficulty)
        
        # Penalize if prerequisites are missing
        if unmet_prereqs:
            raw_roi *= 0.65

        # Projected Readiness Delta (realistic non-guaranteed projection: +3 to +8)
        projected_delta_min = max(2, int(round((total_magnitude_addressed * 1.5) * ev_val)))
        projected_delta_max = projected_delta_min + 3

        ranked_actions.append({
            "action_id": intervention["id"],
            "title": intervention["title"],
            "action_type": intervention["action_type"],
            "primary_gap": intervention["primary_gap"],
            "multi_gap_closure_count": len(addressed_gaps),
            "addressed_gaps": addressed_gaps,
            "estimated_effort_hours": f"{intervention['estimated_hours_min']}-{intervention['estimated_hours_max']} hours",
            "evidence_value_tier": "HIGH" if ev_val >= 0.9 else "MEDIUM",
            "difficulty": "ADVANCED" if difficulty > 1.3 else ("INTERMEDIATE" if difficulty > 1.1 else "FOUNDATIONAL"),
            "roi_score": round(raw_roi, 1),
            "prerequisites": {
                "has_unmet_prerequisites": len(unmet_prereqs) > 0,
                "unmet_prerequisites": unmet_prereqs
            },
            "preview": {
                "current_readiness": current_readiness,
                "projected_readiness_range": f"{current_readiness + projected_delta_min}-{current_readiness + projected_delta_max}",
                "projected_delta": f"+{projected_delta_min} to +{projected_delta_max}",
                "confidence": "MEDIUM"
            },
            "why_this_action": f"Closes {len(addressed_gaps)} competencies including your major constraint ({intervention['primary_gap']}) with verified {intervention['action_type']} proof.",
            "deliverable": intervention["deliverable_type"]
        })

    # Sort descending by ROI score
    ranked_actions.sort(key=lambda a: a["roi_score"], reverse=True)

    top_action = ranked_actions[0] if ranked_actions else None

    return {
        "target_role": target_role_name,
        "current_readiness": current_readiness,
        "total_actions_evaluated": len(ranked_actions),
        "highest_roi_action": top_action,
        "ranked_interventions": ranked_actions
    }
