from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional

from api.deps import get_db, get_current_active_user
from db.models import User
from services.career_digital_twin_service import generate_career_digital_twin_snapshot
from services.evidence_graph_service import (
    trace_skill_lineage, detect_evidence_conflicts
)
from services.canonical_skill_service import get_skill_relationships
from services.career_events_service import get_career_events_timeline
from services.role_comparison_service import compute_candidate_role_alignment

router = APIRouter()

@router.get("")
async def get_career_digital_twin(
    target_role: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Returns the canonical Career Digital Twin snapshot for the authenticated candidate.
    """
    return await generate_career_digital_twin_snapshot(current_user.id, target_role, db)

@router.get("/skills")
async def get_career_twin_skills(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Retrieves candidate's evidence-based skill inventory with taxonomy relationships and conflict detection.
    """
    snapshot = await generate_career_digital_twin_snapshot(current_user.id, None, db)
    skills = snapshot.get("skills_inventory", {}).get("skills", [])

    detailed_skills = []
    for s in skills:
        skill_name = s["skill_name"]
        conflict_report = await detect_evidence_conflicts(current_user.id, skill_name, db)
        relationships = get_skill_relationships(skill_name)
        detailed_skills.append({
            **s,
            "conflict_report": conflict_report,
            "relationships": relationships
        })

    return {
        "candidate_id": str(current_user.id),
        "total_skills": len(detailed_skills),
        "skills": detailed_skills
    }

@router.get("/evidence")
async def get_career_twin_evidence(
    skill_name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Returns granular evidence items with lineage provenance and freshness state.
    """
    if skill_name:
        return await trace_skill_lineage(current_user.id, skill_name, db)
    
    from db.models import EvidenceItem
    from sqlalchemy import select
    stmt = select(EvidenceItem).where(EvidenceItem.user_id == current_user.id).order_by(EvidenceItem.observed_at.desc())
    items = list((await db.execute(stmt)).scalars().all())

    if not items:
        return {
            "candidate_id": str(current_user.id),
            "total_evidence_items": 0,
            "evidence_items": [],
        }

    return {
        "candidate_id": str(current_user.id),
        "total_evidence_items": len(items),
        "evidence_items": [
            {
                "id": str(it.id),
                "skill_name": it.skill_name,
                "evidence_type": it.evidence_type,
                "source": it.source,
                "source_span": it.source_span,
                "source_group": it.source_group,
                "status": it.status,
                "confidence": it.confidence,
                "freshness_state": it.freshness_state,
                "observed_at": it.observed_at.isoformat() if it.observed_at else None
            }
            for it in items
        ]
    }

@router.get("/roles")
async def get_career_twin_role_alignment(
    target_role: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Evaluates candidate alignment against target role requirements with MATCHED, PARTIAL, GAP, and UNKNOWN distinctions.
    """
    role_to_check = target_role or "Backend Engineer"
    return await compute_candidate_role_alignment(current_user.id, role_to_check, db)

@router.get("/trajectory")
async def get_career_twin_trajectory(
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Returns the chronological progression timeline of career events for the candidate.
    """
    events = await get_career_events_timeline(current_user.id, limit, db)
    return events or []

@router.get("/change-feed")
async def get_career_twin_change_feed_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Returns the explainable 'What Changed?' feed for the candidate's Career Digital Twin.
    """
    from services.career_digital_twin_service import get_career_twin_change_feed
    return await get_career_twin_change_feed(current_user.id, db)

@router.get("/forecast")
async def get_career_twin_forecast_endpoint(
    target_role: Optional[str] = Query(None),
    hours_per_week: float = Query(8.0, ge=1.0, le=40.0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Computes a 3, 6, 12 month multi-scenario trajectory forecast (Most Likely, Optimistic, Risk).
    """
    from services.career_readiness_engine import forecast_career_trajectory
    role = target_role or "Backend Engineer"
    return await forecast_career_trajectory(current_user.id, role, hours_per_week, [3, 6, 12], db)

@router.get("/conflicts")
async def get_career_twin_conflicts_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Scans for active cross-source evidentiary contradictions (e.g. claim vs assessment).
    """
    from services.evidence_graph_service import detect_all_evidence_conflicts
    return await detect_all_evidence_conflicts(current_user.id, db)

@router.get("/transitions")
async def get_career_twin_transitions_endpoint(
    current_role: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Evaluates skill transferability bridges across all standard roles to identify minimal-learning paths.
    """
    from services.role_intelligence_service import compute_career_transition_bridges
    from db.models import SkillEvidence
    from sqlalchemy import select
    
    stmt = select(SkillEvidence).where(SkillEvidence.user_id == current_user.id)
    skills = list((await db.execute(stmt)).scalars().all())
    skill_map = {s.skill_name: float(s.score or 75.0) for s in skills}

    role = current_role or "Backend Engineer"
    return compute_career_transition_bridges(role, skill_map)
