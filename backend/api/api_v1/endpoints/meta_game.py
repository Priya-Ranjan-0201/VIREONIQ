from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_current_active_user
from db.models import User
from pydantic import BaseModel
from datetime import datetime, date

from services import meta_game_service

router = APIRouter()

class RejectionRequest(BaseModel):
    company_name: str
    rejection_date: date

@router.get("/hiring-cycle")
async def get_hiring_cycle(
    company_name: str = Query(...),
    role_category: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Retrieve seasonal hiring telemetry, callback multipliers, and application window recommendations.
    """
    res = await meta_game_service.get_hiring_cycle_intelligence(company_name, role_category, db)
    return {
        "status": "success",
        "peak_months": res.peak_months,
        "trough_months": res.trough_months,
        "avg_response_days": res.avg_response_days,
        "competition_multiplier": res.competition_multiplier,
        "timing_recommendation": res.timing_recommendation
    }

@router.post("/rejection-recovery")
async def rejection_recovery(
    req: RejectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Generate email follow-up templates scheduled for 1, 60, and 180 days.
    """
    res = await meta_game_service.generate_rejection_recovery_sequence(
        str(current_user.id),
        req.company_name,
        req.rejection_date,
        db
    )
    return {
        "status": "success",
        "stages": [
            {"day": 1, "send_date": res.stage_1_date.isoformat(), "message": res.stage_1_msg},
            {"day": 60, "send_date": res.stage_2_date.isoformat(), "message": res.stage_2_msg},
            {"day": 180, "send_date": res.stage_3_date.isoformat(), "message": res.stage_3_msg}
        ]
    }

@router.get("/day-of-plan")
async def get_day_of_plan(
    target_company: str = Query(...),
    target_role: str = Query(...),
    interview_datetime: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Generate custom checklist/timeline protocol for candidate preparation on the interview day.
    """
    res = await meta_game_service.generate_day_of_interview_protocol(
        str(current_user.id),
        target_company,
        target_role,
        interview_datetime,
        db
    )
    return {
        "status": "success",
        "best_session_info": res.best_session_info,
        "timeline": {
            "one_hour_before": res.one_hour_before,
            "thirty_min_before": res.thirty_min_before,
            "ten_min_before": res.ten_min_before,
            "post_interview_instruction": res.post_interview_instruction
        }
    }
