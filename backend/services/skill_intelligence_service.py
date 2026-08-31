"""
Skill Intelligence Service.
Authoritative engine for Evidence-Based Skill Intelligence across the 5-tier hierarchy:
  CLAIMED -> INFERRED -> DEMONSTRATED -> ASSESSED -> VERIFIED.
Includes evidence freshness decay, multi-source provenance, and explainable score generation.
"""

import uuid
import math
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from db.models import SkillEvidence, User, Resume, AssessmentResult, ProjectEvidence

logger = logging.getLogger(__name__)

EVIDENCE_TIER_WEIGHTS = {
    "CLAIMED": 0.30,
    "INFERRED": 0.50,
    "DEMONSTRATED": 0.75,
    "ASSESSED": 0.90,
    "VERIFIED": 1.00
}

CONFIDENCE_TIERS = {
    "CLAIMED": "LOW",
    "INFERRED": "LOW",
    "DEMONSTRATED": "MEDIUM",
    "ASSESSED": "HIGH",
    "VERIFIED": "HIGH"
}

DECAY_LAMBDA_PER_MONTH = 0.04 # Halflife ~17 months

def calculate_freshness(last_verified_at: Optional[datetime]) -> float:
    """
    Computes evidence freshness factor (0-100) using exponential temporal decay.
    """
    if not last_verified_at:
        return 50.0
    now = datetime.now(timezone.utc)
    if last_verified_at.tzinfo is None:
        last_verified_at = last_verified_at.replace(tzinfo=timezone.utc)
    days_old = max(0, (now - last_verified_at).total_seconds() / 86400.0)
    months_old = days_old / 30.0
    decay = math.exp(-DECAY_LAMBDA_PER_MONTH * months_old)
    return round(max(10.0, min(100.0, 100.0 * decay)), 2)

async def get_candidate_skill_profile(user_id: uuid.UUID, db: AsyncSession) -> List[Dict[str, Any]]:
    """
    Retrieves candidate's verified skill inventory with evidence provenance and freshness.
    """
    stmt = select(SkillEvidence).where(SkillEvidence.user_id == user_id).order_by(SkillEvidence.score.desc())
    records = (await db.execute(stmt)).scalars().all()
    
    results = []
    for r in records:
        freshness = calculate_freshness(r.last_verified_at)
        results.append({
            "id": str(r.id),
            "skill_name": r.skill_name,
            "evidence_tier": r.evidence_tier,
            "source_type": r.source_type,
            "score": float(r.score or 0.0),
            "confidence": r.confidence,
            "evidence_count": r.evidence_count or 1,
            "evidence_details": r.evidence_details or [],
            "last_verified_at": r.last_verified_at.isoformat() if r.last_verified_at else None,
            "freshness_score": freshness,
            "explanation": r.explanation or f"{r.skill_name} established at {r.evidence_tier} tier with {r.evidence_count} evidence item(s)."
        })
    return results

async def sync_skills_from_resume(user_id: uuid.UUID, parsed_resume: Dict[str, Any], db: AsyncSession) -> int:
    """
    Ingests skills from parsed resume text as CLAIMED or INFERRED evidence.
    """
    raw_skills = parsed_resume.get("skills", [])
    if isinstance(raw_skills, str):
        raw_skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
        
    projects = parsed_resume.get("projects", [])
    project_text = str(projects).lower()
    
    synced_count = 0
    now = datetime.now(timezone.utc)
    
    for skill in raw_skills:
        skill_name = str(skill).strip()
        if not skill_name or len(skill_name) > 100:
            continue
            
        # Determine initial tier: INFERRED if mentioned in project description, else CLAIMED
        is_in_projects = skill_name.lower() in project_text
        tier = "INFERRED" if is_in_projects else "CLAIMED"
        base_score = 65.0 if is_in_projects else 45.0
        
        # Check if already exists in DB
        stmt = select(SkillEvidence).where(
            and_(SkillEvidence.user_id == user_id, SkillEvidence.skill_name.ilike(skill_name))
        )
        existing = (await db.execute(stmt)).scalars().first()
        
        if existing:
            # Only upgrade tier, never downgrade established assessment
            current_tier_rank = list(EVIDENCE_TIER_WEIGHTS.keys()).index(existing.evidence_tier)
            new_tier_rank = list(EVIDENCE_TIER_WEIGHTS.keys()).index(tier)
            if new_tier_rank > current_tier_rank:
                existing.evidence_tier = tier
                existing.score = base_score
                existing.confidence = CONFIDENCE_TIERS[tier]
            existing.evidence_count = (existing.evidence_count or 1) + 1
            existing.last_verified_at = now
            existing.freshness_score = 100.00
        else:
            evidence_item = {
                "source": "Resume Parser",
                "type": "RESUME_KEYWORD_EXTRACTION",
                "context": f"Parsed from resume skill section (Project context: {is_in_projects})",
                "timestamp": now.isoformat()
            }
            new_evidence = SkillEvidence(
                user_id=user_id,
                skill_name=skill_name,
                evidence_tier=tier,
                source_type="RESUME",
                score=base_score,
                confidence=CONFIDENCE_TIERS[tier],
                evidence_count=1,
                evidence_details=[evidence_item],
                last_verified_at=now,
                freshness_score=100.00,
                explanation=f"Established as {tier} via resume ingestion. {skill_name} is {'contextualized in project experience' if is_in_projects else 'listed as claimed competency'}."
            )
            db.add(new_evidence)
            synced_count += 1
            
    await db.commit()
    return synced_count

async def record_assessment_skill_evidence(
    user_id: uuid.UUID,
    skill_name: str,
    assessment_title: str,
    score: float,
    runtime_complexity: str,
    integrity_score: float,
    db: AsyncSession
) -> SkillEvidence:
    """
    Elevates a skill to ASSESSED or VERIFIED upon completing a coding sandbox or technical challenge.
    """
    now = datetime.now(timezone.utc)
    is_verified = (integrity_score >= 85.0 and score >= 80.0)
    tier = "VERIFIED" if is_verified else "ASSESSED"
    
    stmt = select(SkillEvidence).where(
        and_(SkillEvidence.user_id == user_id, SkillEvidence.skill_name.ilike(skill_name))
    )
    existing = (await db.execute(stmt)).scalars().first()
    
    evidence_entry = {
        "source": "Coding Sandbox Assessment",
        "assessment_title": assessment_title,
        "score": score,
        "runtime_complexity": runtime_complexity,
        "integrity_score": integrity_score,
        "timestamp": now.isoformat()
    }
    
    if existing:
        existing.evidence_tier = tier
        existing.source_type = "CODING_LAB"
        existing.score = max(float(existing.score or 0.0), score)
        existing.confidence = "HIGH"
        existing.evidence_count = (existing.evidence_count or 1) + 1
        
        details = list(existing.evidence_details or [])
        details.append(evidence_entry)
        existing.evidence_details = details
        existing.last_verified_at = now
        existing.freshness_score = 100.00
        existing.explanation = (
            f"Evaluated via controlled assessment '{assessment_title}'. "
            f"Achieved {score:.1f}/100 with {runtime_complexity} complexity and {integrity_score:.1f}% integrity score."
        )
        skill_record = existing
    else:
        skill_record = SkillEvidence(
            user_id=user_id,
            skill_name=skill_name,
            evidence_tier=tier,
            source_type="CODING_LAB",
            score=score,
            confidence="HIGH",
            evidence_count=1,
            evidence_details=[evidence_entry],
            last_verified_at=now,
            freshness_score=100.00,
            explanation=f"Demonstrated in controlled assessment '{assessment_title}' with {score:.1f}/100 score."
        )
        db.add(skill_record)
        
    await db.commit()
    return skill_record
