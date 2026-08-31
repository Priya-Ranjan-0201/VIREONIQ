import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from db.session import get_db
from api import deps
from db.models import User, RealInterviewDebrief, CompanyTruthAggregate
from services import truth_db_service, gamification_service
from core.redis import redis_client
from pydantic import BaseModel, Field

router = APIRouter()

class SubmitDebriefRequest(BaseModel):
    company_name: str
    role: str
    interview_date: datetime
    round_type: str
    difficulty: str
    outcome: str
    topics_tested: List[str]
    specific_questions: List[str] = []
    what_worked: str
    what_did_not_work: str
    would_change: str
    is_anonymous: bool = True

@router.get("/search")
async def search_truth(
    query: Optional[str] = None,
    role_category: Optional[str] = None,
    min_submissions: int = Query(5, ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Public search for company aggregates.
    """
    filters = {
        "role_category": role_category,
        "min_submissions": min_submissions
    }
    results = await truth_db_service.search_truth_database(
        query=query,
        filters=filters,
        db=db
    )
    return results

@router.get("/company/{company_name}/{role_category}")
async def get_company_details(
    company_name: str,
    role_category: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns full aggregate insights for a company and role category.
    """
    # Trigger aggregation check
    agg = await truth_db_service.aggregate_company_insights(company_name, role_category, db)
    if not agg:
        # Check current count
        from sqlalchemy import and_
        stmt = select(func.count(RealInterviewDebrief.id)).where(
            and_(
                RealInterviewDebrief.company_name.ilike(f"%{company_name}%"),
                RealInterviewDebrief.role.ilike(f"%{role_category}%")
            )
        )
        # Helper trick to execute count
        stmt_count = select(RealInterviewDebrief).where(
            and_(
                RealInterviewDebrief.company_name.ilike(f"%{company_name}%"),
                RealInterviewDebrief.role.ilike(f"%{role_category}%")
            )
        )
        res = (await db.execute(stmt_count)).scalars().all()
        count = len(res)
        return {
            "status": "insufficient_data",
            "submission_count": count,
            "needed": max(0, 5 - count),
            "contribute_url": "/interviews/submit-debrief"
        }
    return agg

@router.post("/submit-debrief")
async def submit_debrief(
    payload: SubmitDebriefRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Allows candidates to submit interview experiences. Awards 30 XP immediately.
    """
    debrief = RealInterviewDebrief(
        user_id=current_user.id,
        company_name=payload.company_name,
        role=payload.role,
        interview_date=payload.interview_date,
        round_type=payload.round_type,
        difficulty=payload.difficulty,
        outcome=payload.outcome,
        topics_tested=payload.topics_tested,
        specific_questions=payload.specific_questions,
        what_worked=payload.what_worked,
        what_did_not_work=payload.what_did_not_work,
        would_change=payload.would_change,
        is_anonymous=payload.is_anonymous,
        xp_reward_given=True,
        is_quality_verified=False
    )
    db.add(debrief)
    
    # Award immediate XP
    await gamification_service.award_xp(
        user_id=str(current_user.id),
        event_type="debrief_submitted", # 30 XP
        db=db,
        redis=redis_client
    )
    
    await db.commit()

    # Trigger background tasks
    background_tasks.add_task(truth_db_service.verify_submission_quality, debrief.id, db)
    background_tasks.add_task(truth_db_service.aggregate_company_insights, payload.company_name, payload.role, db)

    return {
        "debrief_id": debrief.id,
        "xp_awarded": 30,
        "verification_status": "pending"
    }

@router.get("/leaderboard")
async def get_truth_leaderboard(
    db: AsyncSession = Depends(get_db)
):
    """
    Returns top 20 companies by submission count (excludes companies with < 5 submissions).
    """
    stmt = select(CompanyTruthAggregate).where(CompanyTruthAggregate.submission_count >= 5).order_by(desc(CompanyTruthAggregate.submission_count)).limit(20)
    results = (await db.execute(stmt)).scalars().all()
    return results

@router.get("/my-contributions")
async def get_my_contributions(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns authenticated user's submitted debriefs.
    """
    stmt = select(RealInterviewDebrief).where(RealInterviewDebrief.user_id == current_user.id).order_by(desc(RealInterviewDebrief.created_at))
    results = (await db.execute(stmt)).scalars().all()
    return results
