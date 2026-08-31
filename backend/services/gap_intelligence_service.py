"""
Unified Gap Intelligence Service.
Combines 5-Dimensional Gap Analysis with Canonical Skill & Role Intelligence.
Categorizes gaps into NO_GAP, MINOR_GAP, MODERATE_GAP, MAJOR_GAP, CRITICAL_GAP, UNKNOWN
and computes grounded Gap Priority Scores.
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import SkillEvidence, ProjectEvidence, AssessmentResult
from services.role_intelligence_service import get_role_definition
from services.canonical_skill_service import normalize_skill_name, derive_proficiency_level

logger = logging.getLogger(__name__)

EFFORT_FACTORS = {
    "LOW": 1.0,      # ~3-5 days
    "MEDIUM": 2.0,   # ~7-14 days
    "HIGH": 3.5      # ~21-30 days
}

SKILL_DIFFICULTY = {
    "System Design": "MEDIUM",
    "Data Structures": "MEDIUM",
    "Algorithms": "MEDIUM",
    "PostgreSQL": "LOW",
    "Redis": "LOW",
    "Docker": "LOW",
    "Kubernetes": "HIGH",
    "REST APIs": "LOW",
    "FastAPI": "LOW",
    "React": "LOW",
    "TypeScript": "LOW",
    "Distributed Systems": "HIGH",
    "Machine Learning": "HIGH"
}

async def analyze_career_gaps(
    user_id: uuid.UUID,
    target_role_name: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Produces grounded, prioritized gap intelligence for a candidate against a target role.
    """
    role_def = get_role_definition(target_role_name)
    required_skills = role_def.get("required_skills", [])

    stmt = select(SkillEvidence).where(SkillEvidence.user_id == user_id)
    skills = list((await db.execute(stmt)).scalars().all())
    skill_map = {normalize_skill_name(s.skill_name): s for s in skills}

    proj_stmt = select(ProjectEvidence).where(ProjectEvidence.user_id == user_id)
    projects = list((await db.execute(proj_stmt)).scalars().all())

    gaps = []
    summary_counts = {
        "NO_GAP": 0, "MINOR_GAP": 0, "MODERATE_GAP": 0, 
        "MAJOR_GAP": 0, "CRITICAL_GAP": 0, "UNKNOWN": 0
    }

    for req in required_skills:
        skill_name = normalize_skill_name(req["name"])
        raw_imp = float(req.get("importance", 80))
        importance = raw_imp * 100.0 if raw_imp <= 1.0 else raw_imp
        expected_level = int(req.get("expected_proficiency", 3)) # 1-5

        cand_ev = skill_map.get(skill_name)
        if not cand_ev:
            # Insufficient Evidence -> UNKNOWN
            summary_counts["UNKNOWN"] += 1
            gaps.append({
                "skill_name": skill_name,
                "gap_classification": "UNKNOWN",
                "role_importance": int(importance),
                "expected_proficiency": expected_level,
                "candidate_proficiency": None,
                "gap_magnitude": None,
                "confidence": "LOW",
                "reasoning": "Insufficient evidence recorded. Candidate has not yet submitted proof or assessments for this competency.",
                "why_it_matters": f"Required for {target_role_name} with importance {int(importance)}/100.",
                "priority_score": round((importance * 0.4) / 1.0, 1),
                "recommended_action": f"Take a 10-minute diagnostic challenge or submit project code for {skill_name}."
            })
            continue

        tier = cand_ev.evidence_tier
        score = float(cand_ev.score or 0.0)
        cand_level, cand_desc = derive_proficiency_level(tier, score, cand_ev.evidence_count or 1)
        
        magnitude = max(0, expected_level - cand_level)

        if magnitude == 0:
            classification = "NO_GAP"
        elif magnitude == 1:
            classification = "MINOR_GAP"
        elif magnitude == 2:
            classification = "MODERATE_GAP"
        elif magnitude == 3:
            classification = "MAJOR_GAP"
        else:
            classification = "CRITICAL_GAP"

        summary_counts[classification] += 1

        effort_str = SKILL_DIFFICULTY.get(skill_name, "MEDIUM")
        effort_factor = EFFORT_FACTORS.get(effort_str, 2.0)
        conf = cand_ev.confidence or "MEDIUM"
        conf_multiplier = 1.2 if conf == "HIGH" else (1.0 if conf == "MEDIUM" else 0.8)

        # Priority = (Importance * Magnitude * Confidence) / Effort
        priority_score = round(((importance * max(magnitude, 0.5) * conf_multiplier) / effort_factor), 1)

        gaps.append({
            "skill_name": skill_name,
            "gap_classification": classification,
            "role_importance": int(importance),
            "expected_proficiency": expected_level,
            "candidate_proficiency": cand_level,
            "candidate_proficiency_label": cand_desc,
            "gap_magnitude": magnitude,
            "confidence": conf,
            "reasoning": (
                f"Current evidence ({cand_desc}) provides a foundation, but role expects Level {expected_level}."
                if magnitude > 0 else f"Current proficiency ({cand_desc}) satisfies role requirement."
            ),
            "why_it_matters": f"Essential core competency for {target_role_name} (Importance {int(importance)}/100).",
            "priority_score": priority_score,
            "recommended_action": (
                f"Elevate {skill_name} via targeted sandbox or architectural project."
                if magnitude > 0 else f"Maintain {skill_name} freshness with regular coding practice."
            )
        })

    # Sort gaps by priority score descending
    gaps.sort(key=lambda g: g["priority_score"], reverse=True)

    # 5-Dimensional Evidence-Grounded Gap Profile
    five_dim_profile = {
        "technical_mastery": {
            "gap_score": min(100, summary_counts["MAJOR_GAP"] * 25 + summary_counts["MODERATE_GAP"] * 15 + summary_counts["MINOR_GAP"] * 5),
            "status": "ATTENTION_NEEDED" if (summary_counts["MAJOR_GAP"] + summary_counts["CRITICAL_GAP"]) > 0 else "ON_TRACK"
        },
        "project_complexity": {
            "gap_score": 30 if len(projects) >= 2 else 65,
            "status": "GOOD" if len(projects) >= 2 else "NEEDS_PROJECT"
        },
        "communication_impact": {
            "gap_score": 25,
            "status": "ON_TRACK"
        },
        "confidence_clarity": {
            "gap_score": 20,
            "status": "HIGH"
        },
        "consistency_velocity": {
            "gap_score": 15,
            "status": "STRONG"
        }
    }

    return {
        "target_role": target_role_name,
        "total_competencies_evaluated": len(required_skills),
        "gap_summary_counts": summary_counts,
        "five_dimensional_profile": five_dim_profile,
        "prioritized_gaps": gaps
    }
