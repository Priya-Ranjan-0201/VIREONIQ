from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_current_recruiter_user
from db.models import User

from services import employer_b2b_service

router = APIRouter()

@router.get("/hidden-gems")
async def get_hidden_gems(
    limit: int = Query(5),
    db: AsyncSession = Depends(get_db),
    current_recruiter: User = Depends(get_current_recruiter_user)
) -> list:
    """
    Returns high-potential candidates who might not fit traditional credentials screens
    but score exceptionally in placement ready simulations.
    """
    return await employer_b2b_service.get_hidden_gems(db, limit)

@router.get("/bias-free-candidates")
async def get_bias_free_candidates(
    target_role: str = Query(...),
    limit: int = Query(10),
    db: AsyncSession = Depends(get_db),
    current_recruiter: User = Depends(get_current_recruiter_user)
) -> list:
    """
    Returns completely anonymized candidate profiles scored purely on compatibility metric alignment.
    """
    return await employer_b2b_service.get_bias_free_candidates(db, target_role, limit)

@router.get("/match-explanation")
async def get_match_explanation(
    user_id: str = Query(...),
    job_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_recruiter: User = Depends(get_current_recruiter_user)
) -> dict:
    """
    Generates semantic match details explaining why a candidate is suitable for a specific job listing.
    """
    return await employer_b2b_service.explain_candidate_match(user_id, job_id, db)
