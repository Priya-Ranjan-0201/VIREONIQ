import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import SkillEvidence, ProjectEvidence, AssessmentResult
from services.career_readiness_engine import compute_role_career_readiness
from services.career_bottleneck_engine import identify_career_bottlenecks
from services.gap_intelligence_service import analyze_career_gaps
from services.roi_career_optimizer_service import compute_next_best_career_actions
from services.counterfactual_simulation_service import simulate_hypothetical_interventions
from services.skill_intelligence_service import record_assessment_skill_evidence

@pytest.mark.asyncio
async def test_section_58_synthetic_candidate_benchmark(db_session: AsyncSession, test_user):
    """
    Executes the Section 58 Synthetic Candidate Benchmark:
    Candidate: Backend Engineer Aspirant
    Evidence:
      - Python project, FastAPI project, PostgreSQL project
      - Python assessment (92), DSA assessment (88)
      - System Design assessment (65)
    """
    # 1. Seed Projects
    proj1 = ProjectEvidence(
        user_id=test_user.id,
        title="FastAPI Microservices Platform",
        complexity_score=82.0,
        live_url="https://api.example.com",
        technologies=["Python", "FastAPI", "PostgreSQL"]
    )
    proj2 = ProjectEvidence(
        user_id=test_user.id,
        title="PostgreSQL Index & Query Tuning",
        complexity_score=78.0,
        technologies=["PostgreSQL", "SQL"]
    )
    db_session.add_all([proj1, proj2])

    # 2. Seed Assessments
    await record_assessment_skill_evidence(
        user_id=test_user.id,
        skill_name="Python",
        assessment_title="Python Advanced Concurrency",
        score=92.0,
        runtime_complexity="O(N)",
        integrity_score=99.0,
        db=db_session
    )
    await record_assessment_skill_evidence(
        user_id=test_user.id,
        skill_name="Data Structures",
        assessment_title="Algorithms & DSA",
        score=88.0,
        runtime_complexity="O(log N)",
        integrity_score=97.0,
        db=db_session
    )
    await record_assessment_skill_evidence(
        user_id=test_user.id,
        skill_name="System Design",
        assessment_title="System Architecture Baseline",
        score=65.0,
        runtime_complexity="O(1)",
        integrity_score=95.0,
        db=db_session
    )

    # Claimed / Demonstrated skills
    s_fastapi = SkillEvidence(
        user_id=test_user.id, skill_name="FastAPI", evidence_tier="DEMONSTRATED", score=85.0
    )
    s_postgres = SkillEvidence(
        user_id=test_user.id, skill_name="PostgreSQL", evidence_tier="DEMONSTRATED", score=80.0
    )
    db_session.add_all([s_fastapi, s_postgres])
    await db_session.commit()

    # ── VALIDATION 1: Career Readiness & Strengths/Gaps ───────────────────
    readiness = await compute_role_career_readiness(test_user.id, "Backend Engineer", db_session)
    assert readiness["overall_readiness_score"] >= 65
    assert readiness["confidence"] in ("HIGH", "MEDIUM")

    gaps = await analyze_career_gaps(test_user.id, "Backend Engineer", db_session)
    gap_map = {g["skill_name"]: g for g in gaps["prioritized_gaps"]}

    # Python & Data Structures should have NO_GAP / Met
    assert gap_map["Python"]["gap_classification"] == "NO_GAP"
    assert gap_map["Data Structures"]["gap_classification"] == "NO_GAP"

    # System Design should be classified as MINOR_GAP or MODERATE_GAP
    assert gap_map["System Design"]["gap_classification"] in ("MINOR_GAP", "MODERATE_GAP")

    # Kubernetes should be UNKNOWN (Insufficient Evidence)
    if "Kubernetes" in gap_map:
        assert gap_map["Kubernetes"]["gap_classification"] == "UNKNOWN"
        assert "insufficient evidence" in gap_map["Kubernetes"]["reasoning"].lower()

    # ── VALIDATION 2: Bottleneck Engine ──────────────────────────────────
    bottlenecks = await identify_career_bottlenecks(test_user.id, "Backend Engineer", db_session)
    assert bottlenecks["has_bottleneck"] is True
    assert "System Design" in bottlenecks["primary_bottleneck"]["skill_name"] or bottlenecks["primary_bottleneck"]["role_importance"] >= 80

    # ── VALIDATION 3: Highest-ROI Action ─────────────────────────────────
    optimizer = await compute_next_best_career_actions(test_user.id, "Backend Engineer", db_session)
    top_action = optimizer["highest_roi_action"]
    assert top_action is not None
    assert "Distributed" in top_action["title"] or "System" in top_action["title"] or top_action["roi_score"] > 0
    assert "why_this_action" in top_action

    # ── VALIDATION 4: Zero-Mutation Counterfactual Simulation ────────────
    # Snapshot database row counts before simulation
    count_skills_before = len((await db_session.execute(select(SkillEvidence).where(SkillEvidence.user_id == test_user.id))).scalars().all())
    count_assess_before = len((await db_session.execute(select(AssessmentResult).where(AssessmentResult.user_id == test_user.id))).scalars().all())

    sim_result = await simulate_hypothetical_interventions(
        user_id=test_user.id,
        target_role_name="Backend Engineer",
        hypothetical_evidence=[
            {"skill_name": "System Design", "score": 90.0, "tier": "ASSESSED", "action_type": "ASSESS"},
            {"skill_name": "Distributed Systems", "score": 88.0, "tier": "DEMONSTRATED", "action_type": "BUILD"}
        ],
        db=db_session
    )

    # Check simulated projected improvement
    assert sim_result["simulation_mode"] == "IN_MEMORY_ZERO_MUTATION"
    assert sim_result["projected_state"]["projected_readiness_score"] > readiness["overall_readiness_score"]
    assert "+" in sim_result["projected_state"]["readiness_delta"]

    # Verify zero database mutation
    count_skills_after = len((await db_session.execute(select(SkillEvidence).where(SkillEvidence.user_id == test_user.id))).scalars().all())
    count_assess_after = len((await db_session.execute(select(AssessmentResult).where(AssessmentResult.user_id == test_user.id))).scalars().all())

    assert count_skills_after == count_skills_before
    assert count_assess_after == count_assess_before
