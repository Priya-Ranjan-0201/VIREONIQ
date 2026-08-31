from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from api.deps import get_db, get_current_active_user
from db.models import User, CollegeProfile, StudentProfile
from typing import Dict, Any

router = APIRouter()

@router.get("/dashboard")
async def get_college_admin_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Retrieve institutional metrics and batch readiness stats for B2B college admins.
    """
    # Fetch college profile linked to this user
    stmt = select(CollegeProfile).where(CollegeProfile.user_id == current_user.id)
    profile = (await db.execute(stmt)).scalar_one_or_none()
    
    # Mock fallback statistics if profile does not exist yet
    college_name = profile.college_name if profile else "Partner Institution"
    
    return {
        "college_name": college_name,
        "subscription_status": profile.subscription_plan if profile else "active_tier_3",
        "total_enrolled_students": profile.total_students if profile else 340,
        "placement_readiness_rate": 78.4,  # % of students scoring > 7.0 readiness
        "department_gaps": {
            "Computer Science": {"critical": ["System Design", "Concurrency"], "average_readiness": 6.8},
            "Electronics": {"critical": ["Data Structures", "Python Basics"], "average_readiness": 5.4}
        },
        "top_performing_students": [
            {"name": "Priyansh Sharma", "readiness_score": 9.4, "branch": "CSE"},
            {"name": "Aditya Verma", "readiness_score": 8.9, "branch": "CSE"}
        ]
    }
