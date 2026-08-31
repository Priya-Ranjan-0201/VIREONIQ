"""
Daily Career Operating System Service ("Today's Operating System").
Synthesizes today's focused 3-task mission, enforces idempotent task completion,
maintains strict Activity vs Capability separation, and records transactional career events.
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from datetime import datetime, timezone, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from db.models import (
    CareerInterventionPlan, CareerInterventionTask, 
    EvidenceItem, SkillEvidence, ProjectEvidence, User
)
from services.career_events_service import record_career_event
from services.canonical_skill_service import normalize_skill_name
from services.role_mission_catalog import (
    ROLE_MISSION_CATALOG,
    normalize_target_role,
    TOP_25_MNCS
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Comprehensive Multi-Role Daily Mission Intelligence Catalog
# (Full details: HOW, WHERE, WHEN, WHY, TARGET MNCS, BLUEPRINTS & PROOF)
# ---------------------------------------------------------------------------

async def get_todays_career_mission(
    user_id: uuid.UUID,
    target_role: str = "Backend Engineer",
    db: AsyncSession = None,
    refresh: bool = False,
    cycle: int = 0
) -> Dict[str, Any]:
    """
    Retrieves or synthesizes today's 3-task focused Career Mission with complete
    HOW, WHERE, WHEN, WHY, and VERIFIED PROOF details for every student.
    Supports dynamic role switching across all 8 roles, active plan role matching,
    and cyclical task refresh.
    """
    # Normalize role name to canonical key
    normalized_role = normalize_target_role(target_role)
    matched_catalog = (
        ROLE_MISSION_CATALOG.get(normalized_role)
        or ROLE_MISSION_CATALOG.get("Backend Engineer")
    )

    # 1. Fetch active intervention plan if exists
    plan = None
    if db:
        stmt = select(CareerInterventionPlan).where(
            and_(
                CareerInterventionPlan.user_id == user_id,
                CareerInterventionPlan.status == "IN_PROGRESS"
            )
        ).order_by(CareerInterventionPlan.created_at.desc())
        plan = (await db.execute(stmt)).scalars().first()

    # Determine if user's existing plan matches this specific target role
    matches_role = bool(plan and normalize_target_role(plan.target_role) == normalized_role)
    plan_title = plan.title if matches_role else matched_catalog["active_plan_title"]
    rationale = matched_catalog["rationale"]

    # Select primary or alternate quest set based on refresh / cycle
    use_alt = bool((refresh or (cycle % 2 == 1)) and ("tasks_alt" in matched_catalog))
    mission_tasks = matched_catalog["tasks_alt"] if use_alt else matched_catalog["tasks"]

    total_time = sum(t["estimated_minutes"] for t in mission_tasks)
    progress_pct = float(plan.progress_pct or 0.0) if matches_role else 35.0

    return {
        "mission_date": date.today().isoformat(),
        "target_role": normalized_role,
        "active_plan_title": plan_title,
        "tasks_count": len(mission_tasks),
        "total_estimated_minutes": total_time,
        "progress_pct": progress_pct,
        "tasks": mission_tasks,
        "rationale": rationale,
        "cycle": cycle,
        "is_refreshed": use_alt
    }

async def complete_intervention_task(
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Idempotent task completion:
      - Validates task ownership
      - Generates appropriate EvidenceItem (Activity vs Demonstrated)
      - Updates plan progress percentage
      - Invariant: Task completion never causes duplicate evidence or negative score adjustments.
    """
    stmt = select(CareerInterventionTask).where(
        and_(
            CareerInterventionTask.id == task_id,
            CareerInterventionTask.user_id == user_id
        )
    )
    task = (await db.execute(stmt)).scalars().first()
    if not task:
        raise ValueError("Task not found or unauthorized")

    # Idempotency check: If already completed, return existing status without duplicate evidence
    if task.status == "COMPLETED":
        return {
            "task_id": str(task.id),
            "status": "ALREADY_COMPLETED",
            "message": "Task was already completed previously. No duplicate evidence generated.",
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }

    now = datetime.now(timezone.utc)
    task.status = "COMPLETED"
    task.completed_at = now

    # Generate Evidence Atom based on Task Type (Activity vs Capability)
    plan_stmt = select(CareerInterventionPlan).where(CareerInterventionPlan.id == task.plan_id)
    plan = (await db.execute(plan_stmt)).scalars().first()
    target_skill = normalize_skill_name(plan.primary_gap if plan else "System Design")

    if task.task_type in ("BUILD", "PRACTICE"):
        ev = EvidenceItem(
            user_id=user_id,
            skill_name=target_skill,
            evidence_type="PROJECT_CODE",
            source="INTERVENTION_TASK",
            source_reference=str(task.id),
            source_span=f"Completed build task: {task.title}",
            status="DEMONSTRATED",
            confidence="MEDIUM",
            freshness_state="FRESH"
        )
        db.add(ev)
    else:
        # Learning activity evidence
        ev = EvidenceItem(
            user_id=user_id,
            skill_name=target_skill,
            evidence_type="LEARNING_ACTIVITY",
            source="INTERVENTION_TASK",
            source_reference=str(task.id),
            source_span=f"Completed study task: {task.title}",
            status="CLAIMED",
            confidence="LOW",
            freshness_state="FRESH"
        )
        db.add(ev)

    # Recalculate Plan Progress
    all_tasks_stmt = select(CareerInterventionTask).where(CareerInterventionTask.plan_id == task.plan_id)
    all_tasks = list((await db.execute(all_tasks_stmt)).scalars().all())
    completed_count = sum(1 for t in all_tasks if t.status == "COMPLETED") + 1
    new_progress = round((completed_count / max(len(all_tasks), 1)) * 100.0, 1)

    if plan:
        plan.progress_pct = new_progress
        if new_progress >= 100.0:
            plan.status = "COMPLETED"

    await record_career_event(
        user_id=user_id,
        event_type="TASK_COMPLETED",
        event_data={"task_id": str(task.id), "title": task.title, "plan_progress": new_progress},
        actor="CAREER_OS",
        db=db
    )

    await db.commit()

    return {
        "task_id": str(task.id),
        "status": "COMPLETED",
        "title": task.title,
        "evidence_generated": {
            "skill_name": target_skill,
            "evidence_type": ev.evidence_type,
            "status": ev.status
        },
        "plan_progress_pct": new_progress,
        "message": f"Task completed successfully. Generated {ev.status} evidence atom."
    }
