from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Dict, Any, Optional

from api.deps import get_db, get_current_active_user
from db.models import User, SkillEvidence, CareerReadinessScore
from services.outcome_intelligence_service import (
    record_analytics_event, update_candidate_milestone_progression,
    calculate_career_value_funnel, generate_grounded_executive_insights
)

router = APIRouter()

@router.post("/events")
async def ingest_analytics_event(
    event_type: str = Body(..., embed=True),
    resource_id: Optional[str] = Body(None, embed=True),
    metadata: Optional[Dict[str, Any]] = Body(None, embed=True),
    idempotency_key: Optional[str] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Ingests a canonical, versioned analytics event with idempotency support."""
    return await record_analytics_event(
        event_type=event_type,
        actor_id=current_user.id,
        resource_id=resource_id,
        idempotency_key=idempotency_key,
        metadata=metadata,
        db=db
    )

@router.get("/funnel")
async def get_career_value_funnel(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Retrieves conversion rates across the 6-stage Career Value Funnel."""
    return await calculate_career_value_funnel(db)

@router.get("/candidate/progress")
async def get_candidate_career_progress(
    target_role: str = Query("Backend Engineer"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Retrieves candidate's baseline vs current verified readiness and delta."""
    ev_stmt = select(SkillEvidence).where(SkillEvidence.user_id == current_user.id)
    evidences = list((await db.execute(ev_stmt)).scalars().all())

    tier_counts: Dict[str, int] = {"CLAIMED": 0, "INFERRED": 0, "DEMONSTRATED": 0, "ASSESSED": 0, "VERIFIED": 0}
    for ev in evidences:
        tier = (ev.evidence_tier or "CLAIMED").upper()
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    cri_stmt = (
        select(CareerReadinessScore)
        .where(
            CareerReadinessScore.user_id == current_user.id,
            CareerReadinessScore.target_role == target_role,
        )
        .order_by(desc(CareerReadinessScore.created_at))
        .limit(1)
    )
    latest_cri = (await db.execute(cri_stmt)).scalars().first()
    if latest_cri is not None:
        current_readiness = round(float(latest_cri.overall_readiness or 0.0), 1)
    elif evidences:
        current_readiness = round(
            sum(float(ev.score or 0.0) for ev in evidences) / len(evidences), 1
        )
    else:
        current_readiness = 0.0

    verified_count = tier_counts["VERIFIED"] + tier_counts["ASSESSED"]
    funnel_stage = "VERIFIED_EVIDENCE_READY" if verified_count > 0 else "TWIN_CREATED"

    return await update_candidate_milestone_progression(
        user_id=current_user.id,
        target_role=target_role,
        current_readiness=current_readiness,
        evidence_tier_breakdown=tier_counts,
        funnel_stage=funnel_stage,
        db=db,
    )

@router.get("/executive-insights")
async def get_executive_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Retrieves evidence-grounded executive summaries with mathematical verification."""
    return await generate_grounded_executive_insights(db)
