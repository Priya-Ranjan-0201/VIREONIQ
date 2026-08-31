from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from api import deps
from db.session import get_db
from db.models import User
from services import war_room_service

router = APIRouter()

@router.get("/report/{college_id}", response_model=Dict[str, Any])
async def get_war_room_report(
    college_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_faculty_or_admin)
) -> Dict[str, Any]:
    """Retrieves the placement readiness report, distribution gaps, and probability forecast for the institution."""
    report = await war_room_service.get_college_readiness_report(
        college_id=college_id,
        db=db
    )
    return report
