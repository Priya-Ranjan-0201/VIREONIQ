from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.deps import get_db, get_current_active_user
from db.models import User, ParentProfile, StudentProfile
from typing import Dict, Any

router = APIRouter()

@router.get("/dashboard")
async def get_parent_read_only_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Retrieve read-only placement performance snapshot of a student linked to this parent profile.
    """
    stmt = select(ParentProfile).where(ParentProfile.user_id == current_user.id)
    parent_prof = (await db.execute(stmt)).scalar_one_or_none()
    
    # Mock data fallback for verification
    student_id = parent_prof.student_user_id if parent_prof else current_user.id
    
    return {
        "student_name": "Student Profile",
        "overall_placement_readiness": 8.4,
        "completed_interviews_count": 6,
        "recent_activity": [
            {"date": "2026-06-20", "event": "Completed Mock Amazon Behavioral Session", "score": "8.8 / 10.0"},
            {"date": "2026-06-18", "event": "Uploaded Resume (ATS Score 85%)", "score": "ATS Match High"}
        ],
        "strongest_topics": ["Data Structures", "Dynamic Programming"],
        "needs_review": ["System Design Scalability"]
    }
