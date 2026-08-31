import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import CareerInterventionPlan, CareerInterventionTask, EvidenceItem, SkillEvidence
from services.career_intervention_engine import (
    generate_career_intervention_plan, replan_career_intervention
)
from services.daily_career_os_service import (
    get_todays_career_mission, complete_intervention_task
)
from services.weekly_career_review_service import generate_weekly_career_review

@pytest.mark.asyncio
async def test_multi_strategy_and_time_aware_intervention_generation(db_session: AsyncSession, test_user):
    # 1. Balanced Strategy (14 days, 60m/day)
    plan_bal = await generate_career_intervention_plan(
        user_id=test_user.id,
        target_role="Backend Engineer",
        strategy="BALANCED",
        daily_time_budget_minutes=60,
        db=db_session
    )
    assert plan_bal["duration_days"] == 14
    assert plan_bal["daily_time_budget_minutes"] == 60
    assert plan_bal["status"] == "IN_PROGRESS"
    assert len(plan_bal["tasks"]) >= 5

    # 2. Fastest Strategy (10 days, 90m/day)
    plan_fast = await generate_career_intervention_plan(
        user_id=test_user.id,
        target_role="Backend Engineer",
        strategy="FASTEST",
        daily_time_budget_minutes=90,
        db=db_session
    )
    assert plan_fast["duration_days"] == 10
    assert plan_fast["strategy"] == "FASTEST"

@pytest.mark.asyncio
async def test_idempotent_task_completion_and_activity_separation(db_session: AsyncSession, test_user):
    # Generate Plan
    plan_data = await generate_career_intervention_plan(
        user_id=test_user.id,
        target_role="Backend Engineer",
        strategy="BALANCED",
        daily_time_budget_minutes=60,
        db=db_session
    )
    plan_id = uuid.UUID(plan_data["plan_id"])

    # Fetch first task
    tasks = (await db_session.execute(
        select(CareerInterventionTask).where(CareerInterventionTask.plan_id == plan_id)
    )).scalars().all()
    first_task = tasks[0]

    # 1. First completion
    res1 = await complete_intervention_task(test_user.id, first_task.id, db_session)
    assert res1["status"] == "COMPLETED"
    assert res1["plan_progress_pct"] > 0

    # Verify Evidence atom logged (Activity / Demonstrated)
    ev_atoms = (await db_session.execute(
        select(EvidenceItem).where(EvidenceItem.user_id == test_user.id)
    )).scalars().all()
    assert len(ev_atoms) == 1

    # 2. Duplicate completion (Idempotency test)
    res2 = await complete_intervention_task(test_user.id, first_task.id, db_session)
    assert res2["status"] == "ALREADY_COMPLETED"

    # Evidence atom count must remain 1 (no duplicate creation)
    ev_atoms_after = (await db_session.execute(
        select(EvidenceItem).where(EvidenceItem.user_id == test_user.id)
    )).scalars().all()
    assert len(ev_atoms_after) == 1

@pytest.mark.asyncio
async def test_adaptive_replanning_and_plan_diff(db_session: AsyncSession, test_user):
    plan_data = await generate_career_intervention_plan(
        user_id=test_user.id,
        target_role="Backend Engineer",
        strategy="BALANCED",
        daily_time_budget_minutes=60,
        db=db_session
    )
    plan_id = uuid.UUID(plan_data["plan_id"])

    replan_res = await replan_career_intervention(
        plan_id=plan_id,
        user_id=test_user.id,
        replanning_trigger="ASSESSMENT_PREREQUISITE_IDENTIFIED",
        db=db_session
    )

    assert replan_res["plan_id"] == str(plan_id)
    assert "plan_diff" in replan_res
    assert len(replan_res["plan_diff"]["added_tasks"]) >= 1

@pytest.mark.asyncio
async def test_weekly_career_review_synthesis(db_session: AsyncSession, test_user):
    review = await generate_weekly_career_review(test_user.id, "Backend Engineer", db_session)
    assert "starting_readiness" in review
    assert "ending_readiness" in review
    assert "readiness_delta" in review
    assert "attribution" in review
    assert "next_week_priority" in review
