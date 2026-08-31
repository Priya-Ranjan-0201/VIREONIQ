import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_db
from api import deps
from db.models import User, HighSchoolTrajectory
from services import highschool_service, gamification_service
from core.redis import redis_client
from pydantic import BaseModel, Field

router = APIRouter()

class GenerateHSRequest(BaseModel):
    current_class: int = Field(..., ge=9, le=12)
    target_role: str
    interest_areas: List[str]
    hours_per_week: float = Field(..., ge=1, le=168)

class LogMilestoneRequest(BaseModel):
    year_number: int
    milestone_index: int
    evidence_url: Optional[str] = None

@router.post("/generate-trajectory")
async def generate_trajectory(
    payload: GenerateHSRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates a new years-long roadmap trajectory for the authenticated high school student.
    """
    try:
        traj = await highschool_service.generate_highschool_trajectory(
            user_id=current_user.id,
            current_class=payload.current_class,
            target_role=payload.target_role,
            interest_areas=payload.interest_areas,
            hours_per_week=payload.hours_per_week,
            db=db
        )
        return traj
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/my-trajectory")
async def get_my_trajectory(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns the student's current high school trajectory.
    Auto-initializes starter trajectory if none exists.
    """
    stmt = select(HighSchoolTrajectory).where(HighSchoolTrajectory.user_id == current_user.id)
    traj = (await db.execute(stmt)).scalars().first()
    if not traj:
        try:
            traj = await highschool_service.generate_highschool_trajectory(
                user_id=current_user.id,
                current_class=11,
                target_role="Software Engineer",
                interest_areas=["web development", "algorithms"],
                hours_per_week=5.0,
                db=db
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No trajectory found for this user. Please generate one first."
            )
    return traj

@router.post("/log-milestone")
async def log_milestone(
    payload: LogMilestoneRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logs milestone completions and awards respective XP points.
    """
    stmt = select(HighSchoolTrajectory).where(HighSchoolTrajectory.user_id == current_user.id)
    traj = (await db.execute(stmt)).scalars().first()
    if not traj:
        raise HTTPException(status_code=404, detail="Trajectory profile not found.")

    key = f"{payload.year_number}:{payload.milestone_index}"
    completed = dict(traj.milestones_completed or {})
    if completed.get(key):
        return {"status": "already_completed", "milestones_completed": completed}

    completed[key] = True
    traj.milestones_completed = completed
    db.add(traj)

    # Award milestone XP
    await gamification_service.award_xp(
        user_id=str(current_user.id),
        event_type="hs_milestone_completed", # 50 XP
        db=db,
        redis=redis_client
    )

    # Check if this year's milestones are fully completed
    # Get the plan for this year
    year_plan = None
    for p in (traj.year_plans or []):
        if p.get("year_number") == payload.year_number:
            year_plan = p
            break
            
    if year_plan:
        total_milestones = len(year_plan.get("quarterly_milestones", []))
        completed_this_year = sum(1 for idx in range(total_milestones) if completed.get(f"{payload.year_number}:{idx}"))
        if completed_this_year == total_milestones:
            # Award Year Completed Bonus
            await gamification_service.award_xp(
                user_id=str(current_user.id),
                event_type="hs_year_completed", # 200 XP
                db=db,
                redis=redis_client
            )

    await db.commit()
    return {"status": "success", "milestones_completed": completed}

@router.get("/cohort-benchmarks")
async def get_cohort_benchmarks(
    current_class: int = Query(..., ge=9, le=12),
    target_role: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns aggregate benchmarks for cohort groups.
    """
    res = await highschool_service.get_class_cohort_benchmarks(
        current_class=current_class,
        target_role=target_role,
        db=db
    )
    return res

@router.post("/refresh-for-market")
async def refresh_for_market(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually checks high school trajectory against latest market indicators.
    """
    changes = await highschool_service.update_trajectory_for_market_changes(
        user_id=current_user.id,
        db=db
    )
    return {"status": "success", "changes_applied": changes}
