from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from api.deps import get_db, get_current_active_user
from db.models import User, GamificationProfile
from services import gamification_service
from pydantic import BaseModel
from typing import Optional, List
import uuid

router = APIRouter()

class AwardXPRequest(BaseModel):
    event: str
    custom_xp: Optional[int] = None
    context: Optional[dict] = None

@router.get("/profile")
async def get_gamification_student_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Retrieve the gamification profile for the student (XP, levels, streaks, badges).
    """
    return await gamification_service.get_gamification_profile(db, current_user.id)

@router.post("/award-xp")
async def award_xp_to_student(
    payload: AwardXPRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Award XP to the student for a completed task or activity event.
    """
    return await gamification_service.award_xp(
        db=db,
        user_id=current_user.id,
        event=payload.event,
        custom_xp=payload.custom_xp,
        context=payload.context
    )

@router.get("/leaderboard")
async def get_default_leaderboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Retrieve default global leaderboard sorted by XP."""
    return await get_leaderboard("global", db, current_user)

@router.get("/leaderboard/{leaderboard_type}")
async def get_leaderboard(
    leaderboard_type: str,  # 'global', 'weekly', 'role', 'institution'
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Retrieve ranking leaderboard sorted by XP.
    """
    # Sort key selection
    if leaderboard_type == "weekly":
        order_col = GamificationProfile.weekly_xp
    else:
        order_col = GamificationProfile.total_xp
        
    stmt = select(GamificationProfile).order_by(desc(order_col)).limit(50)
    profiles = (await db.execute(stmt)).scalars().all()
    
    ranks = []
    for idx, p in enumerate(profiles):
        ranks.append({
            "rank": idx + 1,
            "user_id": p.user_id,
            "total_xp": p.total_xp,
            "weekly_xp": p.weekly_xp,
            "current_level": p.current_level,
            "current_streak": p.current_streak_days
        })
        
    return {
        "leaderboard_type": leaderboard_type,
        "rankings": ranks
    }
