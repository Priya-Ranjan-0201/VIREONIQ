from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from db.models import User, Subscription
from api import deps
from sqlalchemy import select

PLAN_FEATURES = {
    "free": {
        "resume_uploads": 3,
        "recommendations_per_month": 5,
        "crm_apps": 10,
        "interview_simulator": False,
        "offer_comparison": False
    },
    "lite": {
        "resume_uploads": 10,
        "recommendations_per_month": 50,
        "crm_apps": 50,
        "interview_simulator": True,
        "offer_comparison": False
    },
    "growth": {
        "resume_uploads": -1, # Unlimited
        "recommendations_per_month": -1,
        "crm_apps": -1,
        "interview_simulator": True,
        "offer_comparison": True
    },
    "premium": {
        "resume_uploads": -1,
        "recommendations_per_month": -1,
        "crm_apps": -1,
        "interview_simulator": True,
        "offer_comparison": True,
        "ai_coach": True
    }
}

async def check_feature_access(
    feature: str,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency to check if a user has access to a specific feature.
    """
    # 1. Fetch user subscription
    sub = (await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )).scalars().first()
    
    plan_id = sub.plan_id if sub else "free"
    plan = PLAN_FEATURES.get(plan_id, PLAN_FEATURES["free"])
    
    if feature not in plan:
        raise HTTPException(status_code=500, detail="Feature configuration error")
        
    access = plan[feature]
    
    if isinstance(access, bool) and not access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Feature '{feature}' requires an upgrade. Current plan: {plan_id.upper()}"
        )
        
    return access
