"""
System endpoints for Feature Flags, Kill Switches, and Health Telemetry (Phase L1).
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from core.feature_flags import feature_flag_engine
from api import deps
from db.models import User

router = APIRouter()


class KillSwitchRequest(BaseModel):
    killed: bool
    reason: str


@router.get("/features", summary="Retrieve active feature flags for current client")
async def get_features(
    current_user: Optional[User] = Depends(deps.get_optional_current_user),
    region: Optional[str] = Query(None, description="Client ISO country or region code"),
) -> Dict[str, Any]:
    user_id = str(current_user.id) if current_user else None
    plan = getattr(current_user, "plan", "free") if current_user else "free"

    active_flags = feature_flag_engine.get_user_flags(
        user_id=user_id,
        plan=plan,
        region=region,
    )
    return {
        "flags": active_flags,
        "environment": "active",
        "authenticated": current_user is not None,
    }


@router.post("/features/{flag_key}/kill-switch", summary="Engage or disengage feature kill switch (Admin only)")
async def set_kill_switch(
    flag_key: str,
    payload: KillSwitchRequest,
    current_user: User = Depends(deps.require_roles(["Admin", "SuperAdmin"])),
) -> Dict[str, Any]:
    actor = f"{current_user.email} (id={current_user.id})"
    success = feature_flag_engine.set_kill_switch(flag_key, payload.killed, actor=actor)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{flag_key}' not recognized.",
        )
    return {
        "status": "success",
        "flag_key": flag_key,
        "kill_switch": payload.killed,
        "reason": payload.reason,
        "updated_by": actor,
    }
