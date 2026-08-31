from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_current_active_user
from db.models import User, PsychometricProfile
from sqlalchemy import select
from core.redis import redis_client
import json

router = APIRouter()

@router.get("/dna")
async def get_student_psychometric_dna(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Retrieve the computed 128-dimensional psychometric placement DNA profile.
    If not ready, returns sessions needed.
    """
    stmt = select(PsychometricProfile).where(PsychometricProfile.user_id == current_user.id)
    profile = (await db.execute(stmt)).scalar_one_or_none()
    
    if not profile or (profile.sessions_completed or 0) < 3:
        needed = 3 - (profile.sessions_completed or 0) if profile else 3
        return {"status": "not_ready", "sessions_needed": max(1, needed)}

    return {
        "status": "ready",
        "profile_type_label": profile.profile_type_label or "The Versatile Analyst",
        "dna_vector": profile.dna_vector,
        "recovery_rate": float(profile.recovery_rate or 0.5),
        "risk_appetite": float(profile.risk_appetite_score or 0.5),
        "persistence": float(profile.persistence_score or 0.5),
        "hire_probabilities": {
            "service": float(profile.hire_prob_service or 0.0),
            "startup": float(profile.hire_prob_startup or 0.0),
            "product": float(profile.hire_prob_product or 0.0),
            "faang": float(profile.hire_prob_faang or 0.0)
        }
    }

@router.get("/twin-results")
async def get_twin_results(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Check Redis for overnight twin simulation matching results.
    """
    user_id = str(current_user.id)
    redis_key = f"twin:results:{user_id}"
    results_str = await redis_client.get(redis_key)
    
    if not results_str:
        return {
            "status": "pending",
            "message": "Results generate overnight after 5 completed sessions"
        }
        
    return {
        "status": "ready",
        "results": json.loads(results_str)
    }

@router.get("/probability-history")
async def get_probability_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> list:
    """
    Returns the placement probability history array for the stock chart.
    """
    stmt = select(PsychometricProfile).where(PsychometricProfile.user_id == current_user.id)
    profile = (await db.execute(stmt)).scalar_one_or_none()
    
    if not profile or not profile.placement_probability_history:
        return []
        
    return profile.placement_probability_history
