"""
Daily Career Mission Service ("What Should I Do Today?").
Generates personalized, actionable daily missions tailored to target role requirements,
current intervention roadmap, and lowest CRI dimensions.
Includes completion tracking, estimated time budgets, and projected readiness point impact.
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from datetime import datetime, timezone, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from db.models import DailyMission, User, Profile
from services.roi_gap_optimizer import calculate_roi_gaps

logger = logging.getLogger(__name__)

async def get_or_generate_daily_mission(
    user_id: uuid.UUID,
    target_role: Optional[str],
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Retrieves or synthesizes today's Career Mission.
    """
    today_str = date.today().isoformat()
    
    # 1. Check if mission already exists for today
    stmt = select(DailyMission).where(
        and_(DailyMission.user_id == user_id, DailyMission.mission_date == today_str)
    )
    mission_obj = (await db.execute(stmt)).scalars().first()
    
    if mission_obj:
        return {
            "id": str(mission_obj.id),
            "mission_date": mission_obj.mission_date,
            "tasks": mission_obj.tasks or [],
            "total_estimated_minutes": mission_obj.total_estimated_minutes or 80,
            "total_projected_delta": float(mission_obj.total_projected_delta or 0.8),
            "completion_rate": float(mission_obj.completion_rate or 0.0),
            "is_completed": mission_obj.is_completed or False
        }

    # 2. Synthesize new personalized mission based on ROI gaps
    role_to_use = target_role or "Backend Engineer"
    gaps = await calculate_roi_gaps(user_id, role_to_use, db)
    top_gap = gaps[0]["skill_name"] if gaps else "System Design"
    second_gap = gaps[1]["skill_name"] if len(gaps) > 1 else "Data Structures"

    tasks = [
        {
            "id": "task_1",
            "title": f"Solve 2 Medium DSA problems focusing on {second_gap}",
            "category": "CODING",
            "estimated_minutes": 35,
            "projected_readiness_delta": 0.35,
            "completed": False,
            "action_url": "/app/coding-interview"
        },
        {
            "id": "task_2",
            "title": f"Complete system architecture module for {top_gap}",
            "category": "ARCHITECTURE",
            "estimated_minutes": 25,
            "projected_readiness_delta": 0.25,
            "completed": False,
            "action_url": "/app/gap-analysis"
        },
        {
            "id": "task_3",
            "title": "Quantify 2 achievements on your active resume draft",
            "category": "RESUME",
            "estimated_minutes": 10,
            "projected_readiness_delta": 0.10,
            "completed": False,
            "action_url": "/app/resume-builder"
        },
        {
            "id": "task_4",
            "title": "Complete 1 simulated behavioral STAR response session",
            "category": "INTERVIEW",
            "estimated_minutes": 10,
            "projected_readiness_delta": 0.10,
            "completed": False,
            "action_url": "/app/interview"
        }
    ]

    total_mins = sum(t["estimated_minutes"] for t in tasks)
    total_delta = sum(t["projected_readiness_delta"] for t in tasks)

    new_mission = DailyMission(
        user_id=user_id,
        mission_date=today_str,
        tasks=tasks,
        total_estimated_minutes=total_mins,
        total_projected_delta=total_delta,
        completion_rate=0.0,
        is_completed=False
    )
    db.add(new_mission)
    await db.commit()

    return {
        "id": str(new_mission.id),
        "mission_date": today_str,
        "tasks": tasks,
        "total_estimated_minutes": total_mins,
        "total_projected_delta": total_delta,
        "completion_rate": 0.0,
        "is_completed": False
    }

async def toggle_task_completion(
    user_id: uuid.UUID,
    task_id: str,
    completed: bool,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Updates the completion status of a specific task within today's mission.
    """
    today_str = date.today().isoformat()
    stmt = select(DailyMission).where(
        and_(DailyMission.user_id == user_id, DailyMission.mission_date == today_str)
    )
    mission_obj = (await db.execute(stmt)).scalars().first()
    
    if not mission_obj:
        mission_obj = await get_or_generate_daily_mission(user_id, None, db)
        return mission_obj

    tasks = list(mission_obj.tasks or [])
    for t in tasks:
        if t.get("id") == task_id:
            t["completed"] = completed
            break

    completed_count = sum(1 for t in tasks if t.get("completed", False))
    completion_rate = (completed_count / max(len(tasks), 1)) * 100.0
    is_all_completed = (completed_count == len(tasks))

    mission_obj.tasks = tasks
    mission_obj.completion_rate = completion_rate
    mission_obj.is_completed = is_all_completed
    
    await db.commit()

    return {
        "id": str(mission_obj.id),
        "mission_date": mission_obj.mission_date,
        "tasks": tasks,
        "completion_rate": completion_rate,
        "is_completed": is_all_completed
    }
