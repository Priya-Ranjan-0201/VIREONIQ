from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List

from api import deps
from db.session import get_db
from db.models import User
from services import pressure_layer_service

router = APIRouter()

@router.get("/check-options", response_model=List[Dict[str, str]])
async def get_check_options(
    current_user: User = Depends(deps.get_current_active_user)
) -> List[Dict[str, str]]:
    """Returns pre-session mood check-in options."""
    return pressure_layer_service.MOOD_CHECK_OPTIONS

@router.post("/mood-checkin", response_model=Dict[str, Any])
async def submit_mood(
    payload: Dict[str, str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Records pre-session mood check-in and adjusts session parameters accordingly."""
    mood_value = payload.get("mood_value")
    if not mood_value:
        raise HTTPException(status_code=400, detail="mood_value is required")

    from core.redis import redis_client
    res = await pressure_layer_service.record_mood_checkin(
        user_id=str(current_user.id),
        mood_value=mood_value,
        db=db,
        redis_client=redis_client
    )
    return res

@router.get("/crisis-contacts", response_model=Dict[str, Any])
async def get_crisis_contacts(
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Returns non-clinical national helpline crisis contacts."""
    return pressure_layer_service.get_crisis_payload()
