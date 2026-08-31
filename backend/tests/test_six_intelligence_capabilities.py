import pytest
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from db.models import (
    Base, Role, User, Profile, SkillEvidence, ProjectEvidence,
    AssessmentResult, MNCInterviewSession, EvidenceItem, CareerGoal
)
from services.evidence_graph_service import (
    compute_skill_evidence_integrity, detect_all_evidence_conflicts, record_granular_evidence
)
from services.canonical_skill_service import (
    compute_multidimensional_skill_mastery, find_true_prerequisite_bottleneck, normalize_skill_name
)
from services.career_readiness_engine import (
    compute_role_career_readiness, forecast_career_trajectory
)
from services.counterfactual_simulation_service import (
    simulate_what_if_query, compare_counterfactual_paths
)
from services.role_intelligence_service import (
    analyze_skill_transferability, compute_career_transition_bridges
)
from services.mnc_interview_intelligence_service import (
    get_user_interview_memory, select_adaptive_next_question,
    start_mnc_interview_session, finalize_mnc_interview_and_sync_twin
)
from services.career_digital_twin_service import (
    generate_career_digital_twin_snapshot, compute_twin_diff, get_career_twin_change_feed
)
from services.career_intervention_engine import generate_next_best_actions

@pytest.fixture
async def test_db():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session
    
    await engine.dispose()


async def create_test_user(db: AsyncSession, email: str = "test@vireoniq.com") -> User:
    role_id = uuid.uuid4()
    role = Role(id=role_id, name=f"Candidate_{uuid.uuid4().hex[:6]}")
    db.add(role)
    await db.flush()

    user_id = uuid.uuid4()
    user = User(id=user_id, email=email, role_id=role_id, is_active=True)
    db.add(user)
    await db.flush()
    return user


@pytest.mark.asyncio
async def test_feature_1_evidence_integrity_and_contradiction_engine(test_db):
    """
    Verifies that the Evidence Integrity Engine computes multi-factor scores and
    generates neutral, non-accusatory conflict cards when claims contradict assessments.
    """
    user = await create_test_user(test_db, "candidate_conflict@vireoniq.com")
    user_id = user.id

    # 1. Add Resume Claim: "Expert Python"
    await record_granular_evidence(
        user_id=user_id,
        skill_name="Python",
        evidence_type="RESUME_CLAIM",
        source="Resume: Senior Developer",
        status="CLAIMED",
        db=test_db
    )

    # 2. Add Failed/Low Coding Assessment: Score = 48/100
    await record_granular_evidence(
        user_id=user_id,
        skill_name="Python",
        evidence_type="CODING_ASSESSMENT",
        source="Python AST Proctored Test",
        status="ASSESSED",
        metadata_payload={"score": 48.0},
        db=test_db
    )

    # 3. Compute Evidence Integrity
    profile = await compute_skill_evidence_integrity(user_id, "Python", test_db)
    assert profile["skill_name"] == "Python"
    assert profile["claim_strength"] == 90.0
    assert profile["assessment_strength"] == 48.0
    assert profile["conflict_score"] > 30.0
    assert profile["integrity_status"] == "CONFLICTED"
    assert profile["verification_required"] is True

    card = profile["conflict_card"]
    assert card is not None
    assert "Resume claim" in card["what_conflicts"]
    assert "calibrated sandbox challenge" in card["resolution_steps"]
    # Verify non-accusatory terminology
    assert "fraud" not in str(card).lower()
    assert "fake" not in str(card).lower()
    assert "dishonest" not in str(card).lower()


@pytest.mark.asyncio
async def test_feature_2_multidimensional_skill_mastery_and_prerequisites():
    """
    Verifies that skills are decomposed into multidimensional sub-dimensions and
    prerequisite bottlenecks are correctly identified.
    """
    # 1. Multidimensional mastery computation
    py_mastery = compute_multidimensional_skill_mastery(
        skill_name="Python",
        base_score=82.0,
        evidence_tier="ASSESSED",
        evidence_count=3
    )
    assert py_mastery["skill_name"] == "Python"
    assert py_mastery["confidence"] == "HIGH"
    assert len(py_mastery["dimensions"]) >= 7
    dim_names = [d["dimension_name"] for d in py_mastery["dimensions"]]
    assert "Syntax & Idioms" in dim_names
    assert "Testing & Mocking" in dim_names

    # 2. Prerequisite dependency bottleneck detection
    # Candidate lacks HTTP & Networking (<65) and wants to learn REST APIs / Microservices
    candidate_skills = {
        "Python": 85.0,
        "HTTP & Networking": 40.0,
        "FastAPI": 75.0
    }
    bottleneck = find_true_prerequisite_bottleneck(candidate_skills, "REST APIs")
    assert bottleneck is not None
    assert bottleneck["bottleneck_skill"].lower() == "http & networking"
    assert bottleneck["current_score"] == 40.0


@pytest.mark.asyncio
async def test_feature_3_career_trajectory_forecasting(test_db):
    """
    Verifies multi-horizon trajectory forecasting with Most Likely, Optimistic, and Risk scenario bounds.
    """
    user = await create_test_user(test_db, "trajectory_test@vireoniq.com")
    user_id = user.id

    forecast = await forecast_career_trajectory(
        user_id=user_id,
        target_role="Backend Engineer",
        hours_per_week=10.0,
        horizons_months=[3, 6, 12],
        db=test_db
    )

    assert forecast["target_role"] == "Backend Engineer"
    assert len(forecast["projections"]) == 3
    
    p3 = forecast["projections"][0]
    assert p3["horizon_months"] == 3
    assert "score_range" in p3["most_likely"]
    assert "score_range" in p3["optimistic"]
    assert "score_range" in p3["risk"]
    # Optimistic should exceed Most Likely, which should exceed Risk
    assert p3["optimistic"]["projected_score"] >= p3["most_likely"]["projected_score"]
    assert p3["most_likely"]["projected_score"] >= p3["risk"]["projected_score"]


@pytest.mark.asyncio
async def test_feature_4_counterfactual_career_simulator(test_db):
    """
    Verifies 'What if I...' query simulation and multi-path comparison matrix.
    """
    user = await create_test_user(test_db, "counterfactual_test@vireoniq.com")
    user_id = user.id

    # 1. Test What-If Query
    what_if = await simulate_what_if_query(
        user_id=user_id,
        target_role="Backend Engineer",
        query_type="LEARN_SKILL",
        query_params={"skill_name": "Kubernetes", "target_score": 88.0, "effort_hours": 25},
        db=test_db
    )
    assert what_if["query_type"] == "LEARN_SKILL"
    assert what_if["estimated_time_cost_hours"] == 25
    assert "simulation_result" in what_if

    # 2. Test Multi-Path Comparison
    comp = await compare_counterfactual_paths(user_id, "Backend Engineer", db=test_db)
    assert comp["total_paths_compared"] == 4
    assert len(comp["comparison_matrix"]) == 4
    assert "roi_efficiency_ratio" in comp["comparison_matrix"][0]


@pytest.mark.asyncio
async def test_feature_5_skill_transfer_intelligence():
    """
    Verifies skill transferability calculations and minimal learning bridge between roles.
    """
    candidate_skills = {
        "Python": 85.0,
        "SQL": 80.0,
        "FastAPI": 75.0,
        "Docker": 70.0,
        "PostgreSQL": 80.0
    }

    # Analyze transfer from Backend Engineer to Data Engineer
    transfer = analyze_skill_transferability(
        current_role="Backend Engineer",
        target_role="Data Engineer",
        candidate_skills=candidate_skills
    )

    assert transfer["current_role"] == "Backend Engineer"
    assert transfer["target_role"] == "Data Engineer"
    assert transfer["transferability_percentage"] >= 40.0
    assert len(transfer["transferable_skills"]) >= 2
    assert "why_this_transition" in transfer["explanations"]

    # Check multiple transitions
    bridges = compute_career_transition_bridges("Backend Engineer", candidate_skills)
    assert len(bridges) > 0
    assert bridges[0]["transferability_percentage"] > 0


@pytest.mark.asyncio
async def test_feature_6_interview_memory_and_adaptive_difficulty(test_db):
    """
    Verifies interview memory cross-session tracking and adaptive difficulty selection.
    """
    user = await create_test_user(test_db, "interview_mem@vireoniq.com")
    user_id = user.id

    # Simulate 2 historical completed sessions
    s1 = MNCInterviewSession(
        id=uuid.uuid4(),
        user_id=user_id,
        target_company="Google",
        target_role="Senior Backend Engineer",
        status="COMPLETED",
        overall_score=72.0,
        dimension_scores={"coding_dsa": 75.0, "system_design": 54.0, "behavioral_star": 86.0}
    )
    s2 = MNCInterviewSession(
        id=uuid.uuid4(),
        user_id=user_id,
        target_company="Google",
        target_role="Senior Backend Engineer",
        status="COMPLETED",
        overall_score=81.0,
        dimension_scores={"coding_dsa": 80.0, "system_design": 68.0, "behavioral_star": 90.0}
    )
    test_db.add_all([s1, s2])
    await test_db.flush()

    # 1. Test Memory Synthesis
    mem = await get_user_interview_memory(user_id, test_db)
    assert mem["total_interviews_completed"] == 2
    assert mem["net_improvement"]["system_design"] == 14.0 # 54 -> 68
    assert "behavioral_star" in mem["mastered_competencies"]
    assert "system_design" in mem["underperforming_competencies"]

    # 2. Test Adaptive Question Selection (targeting underperforming area)
    adaptive_q = await select_adaptive_next_question(
        user_id=user_id,
        target_role="Senior Backend Engineer",
        round_type="SYSTEM_DESIGN",
        current_turn_score=90.0, # High turn score prompts HARD difficulty
        db=test_db
    )
    assert adaptive_q["selected_difficulty"] == "HARD"
    assert adaptive_q["blueprint"]["difficulty"] == "HARD"


@pytest.mark.asyncio
async def test_closed_loop_career_twin_integration(test_db):
    """
    CLOSED LOOP TEST:
    Candidate with Resume Claim -> Low Assessment -> Conflict Detected ->
    Mastery Updated -> Twin Diff / Change Feed -> NBA Generated -> Conflict Resolution -> Twin Elevation.
    """
    user = await create_test_user(test_db, "closed_loop@vireoniq.com")
    user_id = user.id
    profile = Profile(id=uuid.uuid4(), user_id=user_id, first_name="Alex", last_name="Rivera", target_role="Backend Engineer")
    test_db.add(profile)
    await test_db.flush()

    # Step 1: Ingest conflicting claim
    await record_granular_evidence(user_id, "Python", "RESUME_CLAIM", "Resume", status="CLAIMED", db=test_db)
    await record_granular_evidence(user_id, "Python", "CODING_ASSESSMENT", "Test", status="ASSESSED", metadata_payload={"score": 45.0}, db=test_db)

    # Step 2: Generate Twin Snapshot & Verify Conflict
    snap1 = await generate_career_digital_twin_snapshot(user_id, "Backend Engineer", test_db)
    assert snap1["evidence_integrity"]["active_conflicts_count"] >= 1
    assert snap1["evidence_integrity"]["integrity_status"] == "CONFLICT_DETECTED"

    # Step 3: Check Next Best Action prioritization
    nbas = await generate_next_best_actions(user_id, "Backend Engineer", test_db)
    assert len(nbas) > 0
    assert nbas[0]["category"] == "EVIDENCE_INTEGRITY"
    assert "Python" in nbas[0]["title"]

    # Step 4: Resolve conflict with a high-score verified assessment
    await record_granular_evidence(user_id, "Python", "CODING_ASSESSMENT", "Renewal Sandbox Challenge", status="ASSESSED", metadata_payload={"score": 88.0}, db=test_db)
    
    # Also add a project demonstration
    proj = ProjectEvidence(id=uuid.uuid4(), user_id=user_id, title="FastAPI Microservice", complexity_score=90.0, verification_status="VERIFIED")
    test_db.add(proj)
    await test_db.flush()

    # Step 5: Regenerate Twin Snapshot & Compute Diff
    snap2 = await generate_career_digital_twin_snapshot(user_id, "Backend Engineer", test_db)
    diff = compute_twin_diff(snap1, snap2)
    assert diff["input_deltas"]["projects_delta"] >= 1

    # Step 6: Verify Change Feed
    feed = await get_career_twin_change_feed(user_id, test_db)
    assert len(feed) >= 1
    assert any(f["event_type"] == "PROJECT_DEMONSTRATED" for f in feed)
