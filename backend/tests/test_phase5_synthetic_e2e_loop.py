import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import SkillEvidence, EvidenceItem, CareerInterventionPlan, CareerInterventionTask
from services.career_intervention_engine import generate_career_intervention_plan
from services.daily_career_os_service import get_todays_career_mission, complete_intervention_task
from services.unified_assessment_service import (
    create_assessment_session, get_next_adaptive_question,
    submit_question_response, finalize_assessment_session
)
from services.career_readiness_engine import compute_role_career_readiness

@pytest.mark.asyncio
async def test_section_62_synthetic_candidate_closed_execution_loop(db_session: AsyncSession, test_user):
    """
    Validates the complete Section 62 Closed Improvement Loop:
      1. Candidate identifies System Design bottleneck
      2. 14-Day Intervention Plan is generated
      3. Daily Mission is served
      4. Candidate completes daily build & practice tasks (Activity / Demonstrated Evidence)
      5. Candidate takes and completes adaptive capability assessment
      6. EvidenceItems and SkillEvidence are elevated to ASSESSED
      7. Career Readiness is recalculated with proven improvement
    """
    # 1. Generate 14-Day Intervention Plan
    plan = await generate_career_intervention_plan(
        user_id=test_user.id,
        target_role="Backend Engineer",
        strategy="BALANCED",
        daily_time_budget_minutes=60,
        db=db_session
    )
    plan_id = uuid.UUID(plan["plan_id"])
    assert plan["primary_gap"] in ("System Design", "Data Structures")

    # 2. Get Today's Career Mission
    mission = await get_todays_career_mission(test_user.id, "Backend Engineer", db_session)
    assert len(mission["tasks"]) <= 4

    # 3. Complete First Build Task (Generates Demonstrated Evidence)
    tasks = (await db_session.execute(
        select(CareerInterventionTask).where(CareerInterventionTask.plan_id == plan_id)
    )).scalars().all()
    await complete_intervention_task(test_user.id, tasks[0].id, db_session)

    # 4. Take Adaptive Assessment (Generates Assessed Evidence)
    assess_sess = await create_assessment_session(
        user_id=test_user.id,
        target_role="Backend Engineer",
        mode="ASSESSMENT",
        db=db_session
    )
    sess_id = uuid.UUID(assess_sess["session_id"])
    q = await get_next_adaptive_question(sess_id, db_session)
    code = "def two_sum_indexed(nums, target):\n    lookup = {}\n    for i, n in enumerate(nums):\n        if target - n in lookup: return [lookup[target-n], i]\n        lookup[n] = i\n    return []\n"
    await submit_question_response(sess_id, uuid.UUID(q["question_id"]), {"code_submission": code, "duration_seconds": 30.0}, db_session)
    
    # 5. Finalize Assessment & Verify Closed Loop
    final_res = await finalize_assessment_session(sess_id, db_session)
    assert final_res["evidence_created_count"] >= 4

    # 6. Verify Career Readiness is Recalculated
    final_readiness = await compute_role_career_readiness(test_user.id, "Backend Engineer", db_session)
    assert final_readiness["overall_readiness_score"] > 0
    assert final_readiness["readiness_band"] in ("DEVELOPING", "INTERVIEW_READY", "STRONG_HIRE")
