from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from api import deps
from db.session import get_db
from db.models import User, ContentReviewQueue
from services import earn_to_learn_service

router = APIRouter()

@router.get("/my-status", response_model=Dict[str, Any])
async def get_premium_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Returns the user premium tier validity window, lifetime stats, and monthly limits progression."""
    status_data = await earn_to_learn_service.get_user_premium_status(
        user_id=str(current_user.id),
        db=db
    )
    return status_data

@router.get("/contribution-options", response_model=Dict[str, Any])
async def get_contribution_catalog(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Returns all earn-to-learn options, daily/monthly caps, and the student's progress towards them."""
    # Retrieve user specific progression
    status_data = await earn_to_learn_service.get_user_premium_status(
        user_id=str(current_user.id),
        db=db
    )
    
    return {
        "catalog": earn_to_learn_service.CONTRIBUTION_REWARDS,
        "progress": status_data["ledger_this_month"]
    }

@router.post("/submit-vernacular-content", response_model=Dict[str, Any])
async def submit_content(
    payload: Dict[str, str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """
    Submits translated questions or local analogies to the content review queue.
    Successful verification grants the user premium days.
    """
    content_type = payload.get("content_type", "vernacular_analogy")
    content_text = payload.get("content_text")
    target_language = payload.get("target_language", "hi")

    if not content_text:
        raise HTTPException(status_code=400, detail="content_text is required")

    # Save to review queue first
    queue_item = ContentReviewQueue(
        contributor_id=current_user.id,
        content_type=content_type,
        content_text=content_text,
        target_language=target_language,
        status="pending"
    )
    db.add(queue_item)
    await db.flush()

    # Record in the ledger
    res = await earn_to_learn_service.record_contribution(
        user_id=str(current_user.id),
        contribution_type="vernacular_content_contribution",
        reference_id=str(queue_item.id),
        db=db
    )
    return res

@router.post("/check-feature/{feature_name}", response_model=Dict[str, Any])
async def check_feature_gate(
    feature_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Checks whether the student has access to the specified premium feature."""
    has_access = await earn_to_learn_service.check_feature_access(
        user_id=str(current_user.id),
        feature_name=feature_name,
        db=db
    )
    return {
        "feature": feature_name,
        "has_access": has_access,
        "reason": "Premium access required" if not has_access else "Authorized"
    }
