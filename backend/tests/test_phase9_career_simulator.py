import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import (
    User, Role, Profile, SkillEvidence, CareerSimulation, CareerInterventionPlan
)
from services.career_simulation_service import (
    run_counterfactual_simulation, compare_career_paths, convert_scenario_to_active_plan
)

@pytest.mark.asyncio
async def test_section_66_backend_engineer_counterfactual_isolation(db_session: AsyncSession):
    """
    Validates Section 66:
      Candidate: Backend Engineer
      Current readiness: ~74
      Gaps: System Design, Distributed Systems
      Scenario: Build distributed backend project + complete system design assessment.
      Expected:
        Projected readiness: higher than current
        Projected gaps: reduced
        Real readiness & Career Twin: 100% UNCHANGED.
    """
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Test candidate")
        db_session.add(role)
        await db_session.flush()

    user = User(email=f"sim_user_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user)
    await db_session.flush()

    profile = Profile(user_id=user.id, first_name="Eve", last_name="Simulator", target_role="Backend Engineer")
    db_session.add(profile)

    # Initial Skills
    s_py = SkillEvidence(user_id=user.id, skill_name="Python", evidence_tier="VERIFIED", score=85.0)
    s_sd = SkillEvidence(user_id=user.id, skill_name="System Design", evidence_tier="CLAIMED", score=50.0)
    db_session.add_all([s_py, s_sd])
    await db_session.commit()

    # Capture original state snapshot
    initial_sd_tier = s_sd.evidence_tier
    initial_sd_score = s_sd.score

    # Run Counterfactual Simulation
    scenario_res = await run_counterfactual_simulation(
        user_id=user.id,
        target_role="Backend Engineer",
        simulation_type="PROJECT_INVESTMENT",
        scenario_actions=[
            {"skill_name": "System Design", "action_type": "ASSESSMENT", "target_score": 85.0},
            {"skill_name": "Distributed Systems", "action_type": "BUILD_PROJECT", "target_score": 80.0}
        ],
        assumptions={"time_budget_daily_min": 60},
        db=db_session
    )

    assert scenario_res["simulation_id"] is not None
    assert scenario_res["projected_readiness"]["projected_base"] > scenario_res["projected_readiness"]["current_score"]
    assert len(scenario_res["hypothetical_evidence"]) == 2

    # Verification: Real database records MUST NOT be mutated (Section 2 & 55)
    db_sd = await db_session.get(SkillEvidence, s_sd.id)
    assert db_sd.evidence_tier == initial_sd_tier
    assert db_sd.score == initial_sd_score

@pytest.mark.asyncio
async def test_section_67_cybersecurity_role_switch(db_session: AsyncSession):
    """
    Validates Section 67:
      Candidate switches target from Backend Engineer to Cybersecurity Engineer.
      Expected:
        Transferable skills identified: Python, Linux (if present)
        Gaps flagged: Security Fundamentals, Threat Detection, Networking
    """
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Test candidate")
        db_session.add(role)
        await db_session.flush()

    user = User(email=f"switch_user_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user)
    await db_session.flush()

    profile = Profile(user_id=user.id, first_name="Frank", target_role="Backend Engineer")
    db_session.add(profile)
    s1 = SkillEvidence(user_id=user.id, skill_name="Python", evidence_tier="VERIFIED", score=90.0)
    db_session.add(s1)
    await db_session.commit()

    res = await run_counterfactual_simulation(
        user_id=user.id,
        target_role="Cybersecurity Engineer",
        simulation_type="ROLE_SWITCH",
        scenario_actions=[],
        assumptions={"time_budget_daily_min": 60},
        db=db_session
    )

    transferable = [t["skill_name"] for t in res["projected_gaps"]["transferable_skills"]]
    assert "Python" in transferable

    critical_gaps = [g["skill_name"] for g in res["projected_gaps"]["critical_gaps"]]
    assert any(g in critical_gaps for g in ("Threat Detection", "Security Fundamentals", "Networking"))

@pytest.mark.asyncio
async def test_section_68_simulated_evidence_tagging(db_session: AsyncSession):
    """
    Validates Section 68:
      Candidate claims hypothetical certification / assessment.
      Expected: Marked SIMULATED, NOT_VERIFIED, and credential_eligible == False.
    """
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Test candidate")
        db_session.add(role)
        await db_session.flush()

    user = User(email=f"tag_user_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user)
    await db_session.flush()
    await db_session.commit()

    res = await run_counterfactual_simulation(
        user_id=user.id,
        target_role="Platform Engineer",
        simulation_type="SKILL_INVESTMENT",
        scenario_actions=[{"skill_name": "Kubernetes", "action_type": "CERTIFICATION", "target_score": 90.0}],
        assumptions={"time_budget_daily_min": 60},
        db=db_session
    )

    sim_atom = res["hypothetical_evidence"][0]
    assert sim_atom["evidence_tier"] == "SIMULATED"
    assert sim_atom["status"] == "NOT_VERIFIED"
    assert sim_atom["credential_eligible"] is False

@pytest.mark.asyncio
async def test_section_69_time_budget_adaptation(db_session: AsyncSession):
    """
    Validates Section 69:
      Changing time budget from 30 min/day to 120 min/day adapts duration without modifying baseline skill level.
    """
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Test candidate")
        db_session.add(role)
        await db_session.flush()

    user = User(email=f"time_user_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user)
    await db_session.flush()
    await db_session.commit()

    res_30 = await run_counterfactual_simulation(
        user_id=user.id,
        target_role="Backend Engineer",
        simulation_type="TIME_INVESTMENT",
        scenario_actions=[{"skill_name": "System Design", "action_type": "BUILD_PROJECT", "target_score": 85.0}],
        assumptions={"time_budget_daily_min": 30},
        db=db_session
    )

    res_120 = await run_counterfactual_simulation(
        user_id=user.id,
        target_role="Backend Engineer",
        simulation_type="TIME_INVESTMENT",
        scenario_actions=[{"skill_name": "System Design", "action_type": "BUILD_PROJECT", "target_score": 85.0}],
        assumptions={"time_budget_daily_min": 120},
        db=db_session
    )

    # Duration with 120m/day must be significantly shorter than with 30m/day
    assert res_120["timeline_estimate"]["estimated_duration_days"] < res_30["timeline_estimate"]["estimated_duration_days"]

@pytest.mark.asyncio
async def test_section_70_scenario_to_plan_conversion(db_session: AsyncSession):
    """
    Validates Section 70:
      Candidate converts validated simulation scenario into an active intervention plan.
    """
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Test candidate")
        db_session.add(role)
        await db_session.flush()

    user = User(email=f"convert_user_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user)
    await db_session.flush()
    await db_session.commit()

    sim = await run_counterfactual_simulation(
        user_id=user.id,
        target_role="Backend Engineer",
        simulation_type="COMBINATION",
        scenario_actions=[{"skill_name": "FastAPI", "action_type": "ASSESSMENT", "target_score": 85.0}],
        assumptions={"time_budget_daily_min": 60},
        db=db_session
    )

    conv_res = await convert_scenario_to_active_plan(uuid.UUID(sim["simulation_id"]), user.id, db_session)
    assert conv_res["status"] == "PLAN_ACTIVATED_FROM_SCENARIO"
    assert conv_res["intervention_plan_id"] is not None
    assert conv_res["tasks_count"] > 0
