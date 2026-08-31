from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import uuid

from api.deps import get_db, get_current_active_user
from db.models import User, CareerGoal, Profile
from sqlalchemy import select
from services.career_events_service import record_career_event

router = APIRouter()

@router.get("")
async def get_user_career_goals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Retrieves candidate's structured career goals.
    """
    stmt = select(CareerGoal).where(
        CareerGoal.user_id == current_user.id,
        CareerGoal.is_active == True
    ).order_by(CareerGoal.priority.asc())

    goals = list((await db.execute(stmt)).scalars().all())

    return [
        {
            "id": str(g.id),
            "target_role": g.target_role,
            "priority": g.priority,
            "time_horizon": g.time_horizon,
            "experience_level": g.experience_level,
            "preferred_industries": g.preferred_industries or [],
            "preferred_work_mode": g.preferred_work_mode,
            "preferred_locations": g.preferred_locations or []
        }
        for g in goals
    ]

@router.post("")
async def create_or_update_career_goal(
    target_role: str = Body(..., embed=True),
    time_horizon: str = Body("6_MONTHS", embed=True),
    experience_level: str = Body("MID", embed=True),
    preferred_work_mode: str = Body("HYBRID", embed=True),
    preferred_industries: List[str] = Body([], embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Saves a structured user-controlled career aspiration.
    """
    # Deactivate existing goals
    stmt = select(CareerGoal).where(CareerGoal.user_id == current_user.id)
    existing_goals = list((await db.execute(stmt)).scalars().all())
    for eg in existing_goals:
        eg.is_active = False

    new_goal = CareerGoal(
        user_id=current_user.id,
        target_role=target_role,
        priority=1,
        time_horizon=time_horizon,
        experience_level=experience_level,
        preferred_work_mode=preferred_work_mode,
        preferred_industries=preferred_industries,
        is_active=True
    )
    db.add(new_goal)

    # Sync with profile target_role
    prof_stmt = select(Profile).where(Profile.user_id == current_user.id)
    profile = (await db.execute(prof_stmt)).scalars().first()
    if profile:
        profile.target_role = target_role

    await record_career_event(
        user_id=current_user.id,
        event_type="CAREER_GOAL_CHANGED",
        event_data={"target_role": target_role, "time_horizon": time_horizon},
        actor="USER",
        db=db
    )

    await db.commit()

    return {
        "id": str(new_goal.id),
        "target_role": target_role,
        "time_horizon": time_horizon,
        "experience_level": experience_level,
        "preferred_work_mode": preferred_work_mode,
        "preferred_industries": preferred_industries,
        "status": "ACTIVE"
    }

@router.post("/target-role")
async def switch_target_role(
    target_role: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Fast switch of active target role with immediate career event recording.
    """
    prof_stmt = select(Profile).where(Profile.user_id == current_user.id)
    profile = (await db.execute(prof_stmt)).scalars().first()
    if profile:
        profile.target_role = target_role
        await db.commit()

    await record_career_event(
        user_id=current_user.id,
        event_type="TARGET_ROLE_CHANGED",
        event_data={"new_target_role": target_role},
        actor="USER",
        db=db
    )

    return {
        "target_role": target_role,
        "status": "UPDATED"
    }
