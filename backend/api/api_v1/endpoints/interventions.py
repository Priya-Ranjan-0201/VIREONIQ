from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import uuid

from api.deps import get_db, get_current_active_user
from db.models import User, CareerInterventionPlan, CareerInterventionTask, RecommendationFeedback
from sqlalchemy import select, and_
from services.career_intervention_engine import (
    generate_career_intervention_plan, replan_career_intervention
)
from services.daily_career_os_service import (
    get_todays_career_mission, complete_intervention_task
)
from services.weekly_career_review_service import generate_weekly_career_review

router = APIRouter()

@router.post("/generate")
async def generate_plan(
    target_role: str = Body("Backend Engineer", embed=True),
    strategy: str = Body("BALANCED", embed=True, regex="^(FASTEST|BALANCED|HIGH_EVIDENCE|LOWEST_EFFORT|DEEP_MASTERY)$"),
    daily_time_budget_minutes: int = Body(60, ge=15, le=180, embed=True),
    focus_skill: Optional[str] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Generates a personalized, time-aware intervention plan with selectable strategy and custom focus skill.
    """
    return await generate_career_intervention_plan(
        user_id=current_user.id,
        target_role=target_role,
        strategy=strategy,
        daily_time_budget_minutes=daily_time_budget_minutes,
        focus_skill=focus_skill,
        db=db
    )

@router.get("/active")
async def get_active_plan(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Optional[Dict[str, Any]]:
    """
    Retrieves the candidate's current active intervention plan.
    """
    stmt = select(CareerInterventionPlan).where(
        and_(
            CareerInterventionPlan.user_id == current_user.id,
            CareerInterventionPlan.status.in_(["IN_PROGRESS", "PAUSED"])
        )
    ).order_by(CareerInterventionPlan.created_at.desc())
    plan = (await db.execute(stmt)).scalars().first()
    if not plan:
        return None

    return {
        "plan_id": str(plan.id),
        "target_role": plan.target_role,
        "title": plan.title,
        "objective": plan.objective,
        "primary_gap": plan.primary_gap,
        "secondary_gaps": plan.secondary_gaps or [],
        "strategy": plan.strategy,
        "duration_days": plan.duration_days,
        "daily_time_budget_minutes": plan.daily_time_budget_minutes,
        "expected_readiness_delta_range": plan.expected_readiness_delta_range,
        "status": plan.status,
        "progress_pct": float(plan.progress_pct or 0.0),
        "tasks": plan.tasks_data or []
    }

@router.post("/{plan_id}/replan")
async def replan_intervention(
    plan_id: uuid.UUID,
    trigger_reason: str = Body("ASSESSMENT_PREREQUISITE_IDENTIFIED", embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Adapts an existing intervention plan, showing previous vs new plan comparisons.
    """
    return await replan_career_intervention(plan_id, current_user.id, trigger_reason, db)

@router.get("/daily-mission")
async def get_daily_mission(
    target_role: Optional[str] = Query(None),
    refresh: bool = Query(False),
    cycle: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Retrieves today's focused 3-task Career Mission, with dynamic role calibration and refresh support.
    """
    return await get_todays_career_mission(
        current_user.id,
        target_role or "Backend Engineer",
        db,
        refresh=refresh,
        cycle=cycle
    )

@router.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Idempotently marks an intervention task as complete and logs activity evidence.
    """
    return await complete_intervention_task(current_user.id, task_id, db)

@router.post("/feedback")
async def log_feedback(
    intervention_id: Optional[uuid.UUID] = Body(None, embed=True),
    action_id: Optional[str] = Body(None, embed=True),
    feedback_type: str = Body(..., embed=True, regex="^(USEFUL|TOO_DIFFICULT|TOO_EASY|ALREADY_KNOW|NOT_RELEVANT)$"),
    comment: Optional[str] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Logs candidate feedback to improve future intervention recommendation quality.
    """
    fb = RecommendationFeedback(
        user_id=current_user.id,
        intervention_id=intervention_id,
        action_id=action_id,
        feedback_type=feedback_type,
        comment=comment
    )
    db.add(fb)
    await db.commit()
    return {"status": "FEEDBACK_RECORDED", "feedback_type": feedback_type}

@router.get("/weekly-review")
async def get_weekly_review(
    target_role: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Retrieves the synthesized weekly progress review with change attribution.
    """
    return await generate_weekly_career_review(current_user.id, target_role or "Backend Engineer", db)

@router.get("/next-best-actions")
async def get_next_best_actions_endpoint(
    target_role: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Returns prioritized Next Best Actions integrating evidence conflicts, prerequisite bottlenecks, and interview memory.
    """
    from services.career_intervention_engine import generate_next_best_actions
    return await generate_next_best_actions(current_user.id, target_role or "Backend Engineer", db)

@router.get("/explainable-recommendations")
async def get_explainable_recommendations_endpoint(
    target_role: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Returns fully structured, evidence-backed Career Decision Explanations without false precision.
    """
    from services.career_decision_explainability_service import generate_explainable_career_recommendation
    return await generate_explainable_career_recommendation(
        user_id=current_user.id,
        target_role=target_role or "Backend Engineer",
        db=db
    )
