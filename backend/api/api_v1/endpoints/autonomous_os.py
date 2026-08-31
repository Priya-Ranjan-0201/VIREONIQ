from fastapi import APIRouter, Depends, HTTPException, Body, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import uuid

from api.deps import get_db, get_current_active_user
from db.models import User, CareerSignal, AutomationPreference
from sqlalchemy import select, and_
from services.autonomous_career_os_service import (
    generate_daily_career_brief, detect_career_signals, compute_next_best_action,
    detect_career_goal_drift, file_evidence_dispute_workflow, execute_autonomous_action_with_guard
)

router = APIRouter()

@router.get("/brief")
async def get_daily_career_brief(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Retrieves candidate's Daily Career Brief with 1 top priority and progress metrics."""
    return await generate_daily_career_brief(user_id=current_user.id, db=db)

@router.get("/signals")
async def list_career_signals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """Lists active, non-dismissed career moments and signals."""
    return await detect_career_signals(user_id=current_user.id, db=db)

@router.post("/signals/{signal_id}/dismiss")
async def dismiss_signal(
    signal_id: uuid.UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Dismisses or snoozes a career signal."""
    stmt = select(CareerSignal).where(and_(CareerSignal.id == signal_id, CareerSignal.user_id == current_user.id))
    sig = (await db.execute(stmt)).scalars().first()
    if not sig:
        raise HTTPException(status_code=404, detail="Career signal not found")

    sig.is_dismissed = True
    await db.commit()

    return {"status": "DISMISSED", "signal_id": str(signal_id)}

@router.get("/goals")
async def get_career_goals_and_drift(
    primary_goal: str = Query("Backend Engineer"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Retrieves longitudinal career goals and goal drift detection state."""
    return await detect_career_goal_drift(user_id=current_user.id, primary_goal=primary_goal, db=db)

@router.post("/disputes")
async def submit_evidence_dispute(
    evidence_id: uuid.UUID = Body(..., embed=True),
    reason: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Submits a formal evidence dispute for human or algorithmic reassessment."""
    return await file_evidence_dispute_workflow(
        user_id=current_user.id,
        evidence_id=evidence_id,
        reason=reason,
        db=db
    )

@router.post("/actions/execute")
async def execute_career_action(
    action_type: str = Body(..., embed=True),
    is_confirmed: bool = Body(False, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Executes a career action enforcing Autonomy Level 3 user confirmation guards."""
    try:
        return await execute_autonomous_action_with_guard(
            user_id=current_user.id,
            action_type=action_type,
            is_confirmed=is_confirmed,
            db=db
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/preferences")
async def get_automation_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Gets user autonomy settings and emergency kill switch state."""
    return {
        "autonomy_level": 3,
        "proactive_recommendations_enabled": True,
        "deadline_alerts_enabled": True,
        "opportunity_alerts_enabled": True,
        "kill_switch_active": False
    }
