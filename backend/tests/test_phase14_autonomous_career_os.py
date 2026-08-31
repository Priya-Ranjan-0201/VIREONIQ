import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import (
    User, Role, Profile, AssessmentSession, AssessmentEvaluationResult, CareerSignal,
    NextBestAction, CareerGoalRecord, EvidenceDispute
)
from services.autonomous_career_os_service import (
    detect_career_signals, compute_next_best_action, generate_daily_career_brief,
    detect_career_goal_drift, file_evidence_dispute_workflow, execute_autonomous_action_with_guard
)

@pytest.mark.asyncio
async def test_section_138_autonomous_career_loop(db_session: AsyncSession):
    """
    Validates Section 138:
      Autonomous Career OS Loop: Assessment event -> Skill update -> Signal generated -> Next Best Action synthesized.
    """
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Candidate role")
        db_session.add(role)
        await db_session.flush()

    user = User(email=f"autocareer_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user)
    await db_session.flush()

    # 1. Create Assessment Session & Evaluation Result
    session = AssessmentSession(
        id=uuid.uuid4(),
        user_id=user.id,
        target_role="Backend Engineer",
        mode="ASSESSMENT",
        status="COMPLETED"
    )
    db_session.add(session)
    await db_session.flush()

    assess = AssessmentEvaluationResult(
        id=uuid.uuid4(),
        session_id=session.id,
        user_id=user.id,
        target_role="Backend Engineer",
        overall_score=92.0,
        integrity_score=98.0,
        dimension_scores={"SYSTEM_DESIGN": 90.0, "AST_CODE": 94.0}
    )
    db_session.add(assess)
    await db_session.commit()

    # 2. Detect Career Signals
    signals = await detect_career_signals(user.id, db_session)
    assert len(signals) >= 1
    assert any(s["signal_type"] == "SKILL_IMPROVEMENT" for s in signals)

    # 3. Compute Next Best Action (NBA)
    nba = await compute_next_best_action(user.id, target_role="Senior Backend Engineer", db=db_session)
    assert nba["action_type"] == "ASSESSMENT"
    assert "System Design" in nba["title"]
    assert len(nba["why_explanation"]) > 10
    assert nba["feasibility"] == "HIGHLY_FEASIBLE"
    assert nba["action_value_score"] > 80.0

@pytest.mark.asyncio
async def test_section_139_goal_drift_detection(db_session: AsyncSession):
    """
    Validates Section 139:
      Detects when recent candidate activity diverges from stated primary goal.
    """
    user_id = uuid.uuid4()
    drift_res = await detect_career_goal_drift(
        user_id=user_id,
        primary_goal="Backend Engineer",
        recent_activities=["Penetration Testing", "Threat Modeling", "SIEM Architecture"],
        db=db_session
    )
    assert drift_res["primary_goal"] == "Backend Engineer"
    assert drift_res["drift_detected"] is True
    assert drift_res["health_status"] == "AT_RISK"
    assert "Cybersecurity" in drift_res["drift_details"]["detected_trend"]

@pytest.mark.asyncio
async def test_section_140_daily_career_brief(db_session: AsyncSession):
    """
    Validates Section 140:
      Daily Career Brief synthesis with 1 top priority action and progress metrics.
    """
    user_id = uuid.uuid4()
    brief = await generate_daily_career_brief(user_id=user_id, db=db_session)
    assert "today_priority" in brief
    assert brief["today_priority"]["title"] is not None
    assert "progress_telemetry" in brief
    assert brief["safety_guard"] == "AUTONOMY_LEVEL_3_CONFIRMATION_REQUIRED"

@pytest.mark.asyncio
async def test_section_141_autonomy_level_3_safety_guard():
    """
    Validates Section 141 & 143:
      Level 3 Safety Guard: High-impact actions (APPLY_JOB) are strictly blocked without user confirmation.
    """
    user_id = uuid.uuid4()

    # 1. Unconfirmed high-impact action -> Raises PermissionError
    with pytest.raises(PermissionError, match="HIGH_IMPACT_ACTION_BLOCKED"):
        await execute_autonomous_action_with_guard(user_id=user_id, action_type="APPLY_JOB", is_confirmed=False)

    # 2. Confirmed high-impact action -> Allowed
    confirmed_res = await execute_autonomous_action_with_guard(user_id=user_id, action_type="APPLY_JOB", is_confirmed=True)
    assert confirmed_res["execution_status"] == "EXECUTED_WITH_USER_CONFIRMATION"
    assert confirmed_res["autonomy_level"] == 3

@pytest.mark.asyncio
async def test_section_142_low_risk_automation_level_4():
    """
    Validates Section 142 & 144:
      Level 4 Low-Risk Automation: Internal calculation tasks execute automatically.
    """
    user_id = uuid.uuid4()
    auto_res = await execute_autonomous_action_with_guard(user_id=user_id, action_type="RECALCULATE_READINESS")
    assert auto_res["execution_status"] == "EXECUTED_AUTOMATICALLY"
    assert auto_res["autonomy_level"] == 4

@pytest.mark.asyncio
async def test_section_143_evidence_dispute_workflow(db_session: AsyncSession):
    """
    Validates Section 143:
      Registers formal evidence dispute without silent data erasure.
    """
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Candidate role")
        db_session.add(role)
        await db_session.flush()

    user = User(email=f"dispute_user_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user)
    await db_session.flush()

    ev_id = uuid.uuid4()
    dispute = await file_evidence_dispute_workflow(
        user_id=user.id,
        evidence_id=ev_id,
        reason="The AST syntax parser evaluated a valid algorithmic solution as incorrect.",
        db=db_session
    )
    assert dispute["status"] == "OPEN"
    assert "AST syntax parser" in dispute["reason"]
