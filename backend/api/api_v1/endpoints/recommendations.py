from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from schemas.recommendation import JobMatchResponse, UserPreferenceUpdate, UserPreferenceResponse, RecommendationStats
from services.recommendation import matching_engine
from api import deps
from db.models import User, UserPreference, JobListing
from sqlalchemy import select

router = APIRouter()

@router.get("/jobs", response_model=List[JobMatchResponse])
async def get_recommended_jobs(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 10
):
    """
    Get AI-ranked job recommendations with explainability and confidence scores.
    """
    recommendations = await matching_engine.get_job_recommendations(db, current_user, limit)
    return recommendations

@router.post("/preferences", response_model=UserPreferenceResponse)
async def update_preferences(
    prefs_in: UserPreferenceUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user career preferences (Target roles, salary, locations).
    """
    prefs = (await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )).scalars().first()
    
    if not prefs:
        prefs = UserPreference(user_id=current_user.id)
        db.add(prefs)
        
    prefs.target_roles = ",".join(prefs_in.target_roles)
    prefs.preferred_locations = ",".join(prefs_in.preferred_locations)
    prefs.min_salary_target = prefs_in.min_salary_target
    prefs.remote_only = prefs_in.remote_only
    prefs.experience_level = prefs_in.experience_level
    
    await db.commit()
    await db.refresh(prefs)
    
    # Convert comma strings back to lists for response
    return {
        "user_id": prefs.user_id,
        "target_roles": prefs.target_roles.split(","),
        "preferred_locations": prefs.preferred_locations.split(","),
        "min_salary_target": prefs.min_salary_target,
        "remote_only": prefs.remote_only,
        "experience_level": prefs.experience_level
    }

@router.get("/stats", response_model=RecommendationStats)
async def get_employability_stats(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get high-level employability metrics and weekly action plan.
    """
    # Logic to calculate aggregate index
    # (Simplified for MVP)
    return {
        "overall_employability_index": 72.5,
        "market_worth_estimate": "₹8L - ₹12L",
        "top_skill_gaps": ["System Design", "Cloud Infrastructure"],
        "weekly_targets": [
            "Complete 3 system design mock interviews",
            "Apply to 5 High-Growth Startups in Bengaluru",
            "Update Resume with Quantified Project Metrics"
        ]
    }


