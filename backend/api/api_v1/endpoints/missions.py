from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import uuid

from api.deps import get_db, get_current_active_user
from db.models import User
from services.daily_mission_service import get_or_generate_daily_mission, toggle_task_completion
from services.intervention_service import get_active_interventions, generate_prescriptive_intervention

router = APIRouter()

@router.get("/today")
async def get_todays_mission(
    target_role: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Returns today's personalized Career Mission with tasks and projected readiness impact.
    """
    return await get_or_generate_daily_mission(current_user.id, target_role, db)

@router.post("/task-toggle")
async def toggle_mission_task(
    task_id: str = Body(..., embed=True),
    completed: bool = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Toggles completion status for a specific task within today's mission.
    """
    return await toggle_task_completion(current_user.id, task_id, completed, db)

@router.get("/interventions")
async def get_interventions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> list:
    """
    Retrieves active 14-day / 30-day prescriptive intervention pathways.
    """
    return await get_active_interventions(current_user.id, db)

@router.post("/interventions/generate")
async def create_intervention_pathway(
    skill_name: str = Body(..., embed=True),
    duration_days: int = Body(14, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Generates a structured prescriptive intervention roadmap for a specific gap competency.
    """
    return await generate_prescriptive_intervention(current_user.id, skill_name, duration_days, db)
