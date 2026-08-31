from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from db.models import User, UserActivity, Waitlist
from api import deps
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from services import analytics_service

router = APIRouter()

class ActivityLog(BaseModel):
    event_type: str
    metadata_json: Optional[dict] = None

class WaitlistIn(BaseModel):
    email: str
    full_name: str
    referred_by: Optional[str] = None

@router.post("/log")
async def log_activity(
    activity: ActivityLog,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    new_activity = UserActivity(
        user_id=current_user.id,
        event_type=activity.event_type,
        metadata_json=activity.metadata_json
    )
    db.add(new_activity)
    await db.commit()
    return {"status": "logged"}

@router.post("/waitlist/join")
async def join_waitlist(
    data: WaitlistIn,
    db: AsyncSession = Depends(get_db)
):
    entry = Waitlist(
        email=data.email,
        full_name=data.full_name,
        referred_by=data.referred_by
    )
    db.add(entry)
    await db.commit()
    return {"status": "joined"}

@router.get("/overview")
async def get_dashboard_overview(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch aggregated metrics for the user dashboard.
    """
    return await analytics_service.get_user_dashboard_stats(db, current_user.id)

class CareerGPSCalculateRequest(BaseModel):
    target_role: str = "Senior Backend Engineer"
    experience_years: str = "1-3 years"
    target_tier: str = "Tier-1 MNCs (Google, Amazon, Stripe)"
    time_horizon_days: int = 60
    navigation_strategy: str = "FASTEST_PATH"

@router.post("/career-gps/calculate")
async def calculate_career_gps(
    payload: CareerGPSCalculateRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate full turn-by-turn Career GPS Navigation based on candidate inputs.
    """
    return await analytics_service.calculate_career_gps_navigation(
        db=db,
        user_id=current_user.id,
        target_role=payload.target_role,
        experience_years=payload.experience_years,
        target_tier=payload.target_tier,
        time_horizon_days=payload.time_horizon_days,
        strategy=payload.navigation_strategy
    )

