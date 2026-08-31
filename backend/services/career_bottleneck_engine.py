"""
Career Bottleneck Engine.
Identifies the true material bottlenecks constraining candidate readiness for a target role.
Differentiates between low scores in low-importance skills vs critical deficits in high-importance skills:
  Bottleneck Score = Role Importance * Deficit Severity * Dependency Multiplier
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import SkillEvidence
from services.role_intelligence_service import get_role_definition
from services.canonical_skill_service import normalize_skill_name, derive_proficiency_level

logger = logging.getLogger(__name__)

# Prerequisite Dependency Multipliers (Skills that block other skills get higher multiplier)
DEPENDENCY_MULTIPLIERS = {
    "Data Structures": 1.4,
    "Algorithms": 1.4,
    "System Design": 1.3,
    "PostgreSQL": 1.2,
    "SQL": 1.2,
    "Python": 1.2,
    "REST APIs": 1.1,
    "Docker": 1.1,
    "Kubernetes": 1.0,
    "Machine Learning": 1.0
}

async def identify_career_bottlenecks(
    user_id: uuid.UUID,
    target_role_name: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Evaluates role requirements against candidate evidence to pinpoint primary & secondary bottlenecks.
    """
    role_def = get_role_definition(target_role_name)
    required_skills = role_def.get("required_skills", [])

    stmt = select(SkillEvidence).where(SkillEvidence.user_id == user_id)
    skills = list((await db.execute(stmt)).scalars().all())
    skill_map = {normalize_skill_name(s.skill_name): s for s in skills}

    evaluated_constraints = []

    for req in required_skills:
        skill_name = normalize_skill_name(req["name"])
        raw_imp = float(req.get("importance", 80))
        importance = raw_imp * 100.0 if raw_imp <= 1.0 else raw_imp
        expected_level = float(req.get("expected_proficiency", 3)) # 1-5 scale

        cand_ev = skill_map.get(skill_name)
        if not cand_ev:
            # Candidate has zero evidence -> UNKNOWN
            cand_level = 0.0
            deficit_severity = expected_level
            tier = "UNKNOWN"
            is_unknown = True
        else:
            tier = cand_ev.evidence_tier
            score = float(cand_ev.score or 0.0)
            cand_level, _ = derive_proficiency_level(tier, score, cand_ev.evidence_count or 1)
            deficit_severity = max(0.0, expected_level - cand_level)
            is_unknown = False

        if deficit_severity > 0.0 or tier in ("CLAIMED", "INFERRED", "UNKNOWN"):
            dep_mult = DEPENDENCY_MULTIPLIERS.get(skill_name, 1.0)
            # Bottleneck Score = (Importance / 100) * Deficit * Dependency Multiplier
            bottleneck_score = round((importance / 20.0) * (deficit_severity + (0.5 if tier == "CLAIMED" else 0.0)) * dep_mult, 2)

            evaluated_constraints.append({
                "skill_name": skill_name,
                "role_importance": int(importance),
                "expected_level": int(expected_level),
                "candidate_level": int(cand_level) if not is_unknown else None,
                "evidence_tier": tier,
                "deficit_severity": round(deficit_severity, 1),
                "bottleneck_score": bottleneck_score,
                "is_unknown": is_unknown,
                "diagnosis": (
                    f"Insufficient evidence for critical competency (Importance: {int(importance)}/100). Take a baseline evaluation."
                    if is_unknown else
                    f"Proficiency Level {int(cand_level)} is below the expected Level {int(expected_level)} required for {target_role_name}."
                )
            })

    # Sort descending by bottleneck score
    evaluated_constraints.sort(key=lambda x: x["bottleneck_score"], reverse=True)

    primary_bottleneck = evaluated_constraints[0] if evaluated_constraints else None
    secondary_constraints = evaluated_constraints[1:4] if len(evaluated_constraints) > 1 else []

    return {
        "target_role": target_role_name,
        "has_bottleneck": primary_bottleneck is not None,
        "primary_bottleneck": primary_bottleneck,
        "secondary_constraints": secondary_constraints,
        "all_constraints_ranked": evaluated_constraints,
        "bottleneck_summary": (
            f"{primary_bottleneck['skill_name']} is your primary constraint (Importance: {primary_bottleneck['role_importance']}/100, Deficit: {primary_bottleneck['deficit_severity']}). Resolving this will yield maximum readiness improvement."
            if primary_bottleneck else "No significant bottlenecks identified for this role."
        )
    }
