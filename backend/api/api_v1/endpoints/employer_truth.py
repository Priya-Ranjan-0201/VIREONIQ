import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel

from db.session import get_db
from api import deps
from db.models import User, EmployerTruthScore, RealInterviewDebrief
from services import employer_truth_service

router = APIRouter()

class FlagCompanyRequest(BaseModel):
    reason: str

@router.get("/score/{company_name}")
async def get_employer_score(
    company_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns Candidate-Satisfaction ETS score profiles for companies.
    """
    res = await employer_truth_service.compute_employer_truth_score(
        company_name=company_name,
        db=db
    )
    return res

@router.get("/leaderboard/{category}")
async def get_leaderboard(
    category: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns public category leaders (best / worst / most_improved).
    """
    if category not in ["best", "worst", "most_improved"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category must be 'best', 'worst', or 'most_improved'."
        )
    board = await employer_truth_service.get_ets_leaderboard(category=category, db=db)
    return board

@router.post("/flag/{company_name}")
async def flag_company(
    company_name: str,
    payload: FlagCompanyRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Flags companies for reviews and alerts administrators on anomalies.
    """
    await employer_truth_service.flag_company_for_review(
        company_name=company_name,
        reason=payload.reason,
        reported_by=current_user.id,
        db=db
    )
    return {"status": "success", "message": f"Flag submitted for '{company_name}'."}

@router.get("/my-experience-score")
async def get_my_experience_score(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns ETS scores for all companies the authenticated user has interviewed at.
    """
    # Fetch all user's unique companies from debriefs
    stmt = select(RealInterviewDebrief.company_name).where(RealInterviewDebrief.user_id == current_user.id).distinct()
    comps = (await db.execute(stmt)).scalars().all()

    scores = []
    for c in comps:
        stmt_score = select(EmployerTruthScore).where(EmployerTruthScore.company_name == c)
        score = (await db.execute(stmt_score)).scalars().first()
        if score:
            scores.append(score)
            
    return scores
