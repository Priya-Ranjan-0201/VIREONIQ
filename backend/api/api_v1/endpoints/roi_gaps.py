from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import uuid

from api.deps import get_db, get_current_active_user
from db.models import User
from services.gap_intelligence_service import analyze_career_gaps
from services.roi_career_optimizer_service import compute_next_best_career_actions
from services.career_events_service import record_career_event

router = APIRouter()

@router.get("/prioritized")
async def get_prioritized_gaps(
    target_role: Optional[str] = Query("Backend Engineer"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Returns prioritized career gap intelligence with classifications (NO_GAP to UNKNOWN) and priority scores.
    """
    return await analyze_career_gaps(current_user.id, target_role, db)

@router.get("/next-best-actions")
async def get_next_best_career_actions(
    target_role: Optional[str] = Query("Backend Engineer"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Returns ranked high-ROI interventions with multi-gap closure detection and transparent projected impact.
    """
    return await compute_next_best_career_actions(current_user.id, target_role, db)

@router.post("/recommendations/action")
async def record_user_action_decision(
    action_id: str = Body(..., embed=True),
    decision: str = Body(..., embed=True, regex="^(ACCEPT|REJECT|POSTPONE)$"),
    reason: Optional[str] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Records candidate's decision on a career recommendation (ACCEPT, REJECT with reason, or POSTPONE).
    """
    await record_career_event(
        user_id=current_user.id,
        event_type=f"RECOMMENDATION_{decision}",
        event_data={
            "action_id": action_id,
            "decision": decision,
            "reason": reason
        },
        actor="USER",
        db=db
    )

    return {
        "action_id": action_id,
        "decision": decision,
        "status": "RECORDED",
        "message": f"Action {decision.lower()}ed successfully."
    }
