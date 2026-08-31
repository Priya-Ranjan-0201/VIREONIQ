import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from api import deps
from db.models import User, CareerRebirthPlan
from services import rebirth_service
from pydantic import BaseModel, Field

router = APIRouter()

class GenerateRoadmapRequest(BaseModel):
    current_domain: str = Field(..., description="Current domain before transition, e.g. banking_finance")
    target_role: str = Field(..., description="Target tech role, e.g. fintech_analyst")
    available_hours_per_week: float = Field(..., ge=1, le=168)
    career_break_reason: Optional[str] = Field(None, description="Reason for career break if any")
    break_duration_months: Optional[int] = Field(None, ge=0)

class RewriteResumeRequest(BaseModel):
    resume_id: uuid.UUID
    target_role: str

@router.post("/generate")
async def generate_roadmap(
    payload: GenerateRoadmapRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates a personalized, highly structured 6-phase roadmap for a career switcher or returner.
    """
    try:
        plan = await rebirth_service.generate_transition_roadmap(
            user_id=current_user.id,
            current_domain=payload.current_domain,
            target_role=payload.target_role,
            available_hours_per_week=payload.available_hours_per_week,
            career_break_reason=payload.career_break_reason,
            break_duration_months=payload.break_duration_months,
            db=db
        )
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate roadmap: {str(e)}"
        )

@router.get("/my-plan")
async def get_my_plan(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns the authenticated user's transition plan.
    Auto-initializes starter plan if user does not have an active record.
    """
    from sqlalchemy import select
    stmt = select(CareerRebirthPlan).where(CareerRebirthPlan.user_id == current_user.id)
    plan = (await db.execute(stmt)).scalars().first()
    if not plan:
        try:
            plan = await rebirth_service.generate_transition_roadmap(
                user_id=current_user.id,
                current_domain="banking_finance",
                target_role="Data Analyst",
                available_hours_per_week=15,
                career_break_reason=None,
                break_duration_months=0,
                db=db
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transition plan not found. Please generate one first."
            )
    return plan

@router.post("/rewrite-resume")
async def rewrite_resume(
    payload: RewriteResumeRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Rewrites a transitioner's resume to position their past non-tech domain experience as a unique strength.
    """
    try:
        rewritten = await rebirth_service.rewrite_resume_for_transition(
            resume_id=payload.resume_id,
            target_role=payload.target_role,
            db=db
        )
        return rewritten
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rewrite resume: {str(e)}"
        )
