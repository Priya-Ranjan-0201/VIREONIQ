from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, List, Optional
import uuid

from api.deps import get_db, get_current_active_user
from db.models import User, Profile, CareerReadinessScore
from services.career_readiness_engine import compute_role_career_readiness
from services.career_bottleneck_engine import identify_career_bottlenecks

router = APIRouter()

@router.get("")
@router.get("/profile")
async def get_readiness_profile(
    target_role: Optional[str] = Query(None, description="Optional target role override"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Computes canonical 9-Dimensional Career Readiness Index (v3.0.0) with dimension contribution analysis.
    """
    role_to_evaluate = target_role
    if not role_to_evaluate:
        prof_stmt = select(Profile).where(Profile.user_id == current_user.id)
        profile = (await db.execute(prof_stmt)).scalar_one_or_none()
        role_to_evaluate = profile.target_role if (profile and profile.target_role) else "Backend Engineer"
        
    return await compute_role_career_readiness(current_user.id, role_to_evaluate, db)

@router.get("/bottlenecks")
async def get_career_bottlenecks(
    target_role: Optional[str] = Query(None, description="Target role name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Pinpoints primary and secondary career bottlenecks constraining candidate readiness.
    """
    role_to_evaluate = target_role or "Backend Engineer"
    return await identify_career_bottlenecks(current_user.id, role_to_evaluate, db)

@router.get("/history")
async def get_readiness_history(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Retrieves chronological Career Readiness trajectory with change attribution.
    """
    stmt = (
        select(CareerReadinessScore)
        .where(CareerReadinessScore.user_id == current_user.id)
        .order_by(CareerReadinessScore.created_at.asc())
        .limit(limit)
    )
    records = (await db.execute(stmt)).scalars().all()
    
    return [
        {
            "id": str(r.id),
            "target_role": r.target_role,
            "overall_readiness": float(r.overall_readiness or 0.0),
            "technical_capability": float(r.technical_capability or 0.0),
            "project_capability": float(r.project_capability or 0.0),
            "coding_mastery": float(r.coding_mastery or 0.0),
            "system_design": float(r.system_design or 0.0),
            "communication_score": float(r.communication_score or 0.0),
            "interview_readiness": float(r.interview_readiness or 0.0),
            "resume_evidence_strength": float(r.resume_evidence_strength or 0.0),
            "role_alignment": float(r.role_alignment or 0.0),
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]
