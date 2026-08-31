import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import (
    User, Role, Profile, SkillEvidence, RecruiterOrganization,
    OrganizationUnit, OrganizationEmployee, OrganizationCapabilitySnapshot
)
from services.workforce_intelligence_service import (
    calculate_team_capability_coverage, generate_workforce_capability_matrix,
    evaluate_hiring_vs_upskilling, find_internal_talent_mobility,
    simulate_organizational_counterfactual, create_capability_snapshot
)

@pytest.mark.asyncio
async def test_section_78_synthetic_20_person_workforce_capability(db_session: AsyncSession):
    """
    Validates Section 78:
      Organization: DemoTech
      Team: Backend Engineering (20 employees)
      Synthetic Evidence:
        Python: 80% coverage
        System Design: 55% coverage
        Cloud: 72% coverage
        Kubernetes: 31% coverage
      Expected: Kubernetes becomes a critical capability gap.
    """
    # 1. Setup Role
    role_stmt = select(Role).where(Role.name == "employee")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="employee", description="Employee role")
        db_session.add(role)
        await db_session.flush()

    # 2. Setup Organization & Unit
    org = RecruiterOrganization(name=f"DemoTech {uuid.uuid4().hex[:6]}", domain="demotech.io")
    db_session.add(org)
    await db_session.flush()

    unit = OrganizationUnit(organization_id=org.id, name="Backend Engineering", unit_type="TEAM")
    db_session.add(unit)
    await db_session.flush()

    # 3. Create 20 Employees with calibrated evidence
    for i in range(20):
        user = User(email=f"eng_{i}_{uuid.uuid4().hex[:6]}@demotech.io", password_hash="pw", role_id=role.id)
        db_session.add(user)
        await db_session.flush()

        emp = OrganizationEmployee(
            organization_id=org.id,
            unit_id=unit.id,
            user_id=user.id,
            name=f"Engineer {i+1}",
            email=user.email,
            role_title="Backend Engineer"
        )
        db_session.add(emp)

        # Python: 16/20 have strong evidence (~80%)
        if i < 16:
            s_py = SkillEvidence(user_id=user.id, skill_name="Python", evidence_tier="VERIFIED", score=90.0)
            db_session.add(s_py)

        # System Design: 11/20 have moderate evidence (~55%)
        if i < 11:
            s_sd = SkillEvidence(user_id=user.id, skill_name="System Design", evidence_tier="ASSESSED", score=80.0)
            db_session.add(s_sd)

        # Cloud: 14/20 have demonstrated evidence (~70%)
        if i < 14:
            s_cl = SkillEvidence(user_id=user.id, skill_name="Cloud", evidence_tier="DEMONSTRATED", score=85.0)
            db_session.add(s_cl)

        # Kubernetes: 6/20 have evidence (~30%)
        if i < 6:
            s_k8s = SkillEvidence(user_id=user.id, skill_name="Kubernetes", evidence_tier="ASSESSED", score=75.0)
            db_session.add(s_k8s)

    await db_session.commit()

    # 4. Calculate Capability Coverage
    cov = await calculate_team_capability_coverage(unit.id, org.id, db_session)
    assert cov["team_size"] == 20
    assert cov["overall_coverage_pct"] >= 45.0

    # Verify Kubernetes is identified as a critical gap
    k8s_analysis = next((c for c in cov["competencies"] if c["competency"] == "Kubernetes"), None)
    assert k8s_analysis is not None
    assert k8s_analysis["coverage_pct"] < 40.0
    assert k8s_analysis["gap_status"] in ("CRITICAL_GAP", "HIGH_GAP")

    critical_gap_names = [g["competency"] for g in cov["critical_gaps"]]
    assert "Kubernetes" in critical_gap_names

@pytest.mark.asyncio
async def test_section_79_counterfactual_simulation(db_session: AsyncSession):
    """
    Validates Section 79:
      Simulate 3 employees completing Kubernetes intervention.
      Expected: Projected coverage increases. Original snapshot remains unchanged.
    """
    org = RecruiterOrganization(name=f"SimTech {uuid.uuid4().hex[:6]}")
    db_session.add(org)
    await db_session.flush()

    # Take initial baseline snapshot
    initial_snapshot = await create_capability_snapshot(org.id, None, db_session)

    # Run Counterfactual Simulation
    sim_result = await simulate_organizational_counterfactual(
        organization_id=org.id,
        unit_id=None,
        hypothetical_changes={"upskill_count": 3, "target_skill": "Kubernetes"},
        db=db_session
    )

    assert sim_result["projected_overall_coverage"] > sim_result["current_overall_coverage"]
    assert sim_result["projected_coverage_delta"] > 0.0

    # Ensure original snapshot was not modified
    snap_in_db = await db_session.get(OrganizationCapabilitySnapshot, uuid.UUID(initial_snapshot["snapshot_id"]))
    assert snap_in_db.overall_coverage_pct == initial_snapshot["overall_coverage_pct"]

@pytest.mark.asyncio
async def test_section_80_single_point_concentration_risk(db_session: AsyncSession):
    """
    Validates Section 80:
      1 expert in a 20-person team -> HIGH capability concentration risk.
    """
    role_stmt = select(Role).where(Role.name == "employee")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="employee", description="Employee role")
        db_session.add(role)
        await db_session.flush()

    org = RecruiterOrganization(name=f"RiskTech {uuid.uuid4().hex[:6]}")
    db_session.add(org)
    await db_session.flush()

    unit = OrganizationUnit(organization_id=org.id, name="Core Systems", unit_type="TEAM")
    db_session.add(unit)
    await db_session.flush()

    for i in range(10):
        user = User(email=f"user_risk_{i}_{uuid.uuid4().hex[:6]}@risk.io", password_hash="pw", role_id=role.id)
        db_session.add(user)
        await db_session.flush()
        emp = OrganizationEmployee(organization_id=org.id, unit_id=unit.id, user_id=user.id, name=f"Dev {i}", email=user.email)
        db_session.add(emp)

        # Only 1 expert in Distributed Systems
        if i == 0:
            s = SkillEvidence(user_id=user.id, skill_name="Distributed Systems", evidence_tier="VERIFIED", score=95.0)
            db_session.add(s)

    await db_session.commit()

    cov = await calculate_team_capability_coverage(unit.id, org.id, db_session)
    assert cov["concentration_risks_count"] >= 1
    dist_risk = next((r for r in cov["concentration_risks"] if r["competency"] == "Distributed Systems"), None)
    assert dist_risk is not None
    assert dist_risk["expert_count"] == 1
    assert dist_risk["risk_level"] in ("HIGH", "CRITICAL")

@pytest.mark.asyncio
async def test_section_81_unknown_vs_zero_evidence(db_session: AsyncSession):
    """
    Validates Section 81:
      No evidence exists for Cloud Security.
      Expected: UNKNOWN / INSUFFICIENT_EVIDENCE (EVIDENCE_SHORTAGE), never treated as 0% lack of skill.
    """
    org = RecruiterOrganization(name=f"EvidenceTest {uuid.uuid4().hex[:6]}")
    db_session.add(org)
    await db_session.flush()

    cov = await calculate_team_capability_coverage(None, org.id, db_session)
    sec_comp = next((c for c in cov["competencies"] if c["competency"] == "Cloud Security"), None)
    assert sec_comp is not None
    assert sec_comp["gap_status"] == "UNKNOWN_INSUFFICIENT_EVIDENCE"
    assert sec_comp["shortage_type"] == "EVIDENCE_SHORTAGE"

@pytest.mark.asyncio
async def test_section_82_internal_talent_mobility(db_session: AsyncSession):
    """
    Validates Section 82:
      Matches internal employees to a new Platform Engineer role without making autonomous employment decisions.
    """
    role_stmt = select(Role).where(Role.name == "employee")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="employee", description="Employee role")
        db_session.add(role)
        await db_session.flush()

    org = RecruiterOrganization(name=f"MobilityTech {uuid.uuid4().hex[:6]}")
    db_session.add(org)
    await db_session.flush()

    user = User(email=f"candidate_mob_{uuid.uuid4().hex[:6]}@mob.com", password_hash="pw", role_id=role.id)
    db_session.add(user)
    await db_session.flush()

    emp = OrganizationEmployee(organization_id=org.id, user_id=user.id, name="Dan Mobility", email=user.email, role_title="Backend Engineer")
    db_session.add(emp)
    s1 = SkillEvidence(user_id=user.id, skill_name="Python", evidence_tier="VERIFIED", score=90.0)
    s2 = SkillEvidence(user_id=user.id, skill_name="Cloud", evidence_tier="ASSESSED", score=85.0)
    db_session.add_all([s1, s2])
    await db_session.commit()

    mobility = await find_internal_talent_mobility("Platform Engineer", org.id, db_session)
    assert mobility["eligible_internal_candidates_count"] >= 1
    top_cand = mobility["top_internal_matches"][0]
    assert top_cand["name"] == "Dan Mobility"
    assert top_cand["internal_match_score"] >= 70.0
    assert "readiness_recommendation" in top_cand
