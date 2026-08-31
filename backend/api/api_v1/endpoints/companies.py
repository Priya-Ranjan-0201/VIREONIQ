from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_current_active_user
from db.models import User
from services import company_profiles
from typing import List

router = APIRouter()

@router.get("/profiles")
async def get_all_company_profiles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[dict]:
    """
    Retrieve all target company interview simulator profiles.
    """
    profiles = await company_profiles.get_company_profiles(db)
    return [
        {
            "id": p.id,
            "profile_key": p.profile_key,
            "display_name": p.display_name,
            "company_type": p.company_type,
            "interview_stages": p.interview_stages,
            "question_style_weights": p.question_style_weights,
            "difficulty_level": p.difficulty_level,
            "estimated_ctc_min_lpa": float(p.estimated_ctc_min_lpa),
            "estimated_ctc_max_lpa": float(p.estimated_ctc_max_lpa),
            "description": p.description,
            "leadership_principles": p.leadership_principles
        }
        for p in profiles
    ]

@router.get("/{profile_key}/profile")
async def get_single_company_profile(
    profile_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Retrieve details of a single company profile by its key (e.g., google, amazon).
    """
    p = await company_profiles.get_company_profile_by_key(db, profile_key)
    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found."
        )
    return {
        "id": p.id,
        "profile_key": p.profile_key,
        "display_name": p.display_name,
        "company_type": p.company_type,
        "interview_stages": p.interview_stages,
        "question_style_weights": p.question_style_weights,
        "difficulty_level": p.difficulty_level,
        "estimated_ctc_min_lpa": float(p.estimated_ctc_min_lpa),
        "estimated_ctc_max_lpa": float(p.estimated_ctc_max_lpa),
        "description": p.description,
        "leadership_principles": p.leadership_principles
    }
