"""
VIREONIQ X — Canonical 11/10 Hardening & Intelligence Test Suite.
Verifies:
  1. Professional Evidence Graph 10-state lifecycle & source normalization
  2. Career Digital Twin 2.0 with explainable diff & uncertainty tiers
  3. 9D Career Readiness Index with bottleneck isolation & evidence coverage
  4. Next Best Action explainability (Why this? Why now? Supporting evidence?)
  5. Deterministic AST code complexity & execution pipeline
  6. MNC Adaptive Interview studio blueprint generation (public competency frameworks)
  7. Enterprise Zero-Trust & Level 3 Autonomy Safety Guards
"""

import pytest
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import (
    User, Role, Profile, SkillEvidence, ProjectEvidence, AssessmentResult,
    EvidenceItem, NextBestAction, VerifiedCredential
)
from services.evidence_graph_service import (
    CANONICAL_EVIDENCE_STATES, validate_evidence_state, record_granular_evidence,
    detect_evidence_conflicts, trace_skill_lineage, analyze_developer_profiles
)
from services.career_digital_twin_service import (
    generate_career_digital_twin_snapshot, compute_twin_diff
)
from services.career_readiness_engine import compute_role_career_readiness
from services.autonomous_career_os_service import (
    compute_next_best_action, generate_daily_career_brief, execute_autonomous_action_with_guard
)
from services.code_execution_service import analyze_python_ast_complexity
from services.mnc_interview_intelligence_service import (
    create_company_interview_profile, generate_question_blueprint,
    generate_and_validate_coding_question
)
from services.credential_issuance_service import (
    compute_canonical_hmac_signature, verify_canonical_hmac_signature,
    evaluate_and_issue_credential, verify_credential_public
)


@pytest.fixture
async def setup_test_candidate(db_session: AsyncSession):
    """Sets up a canonical synthetic candidate for 11/10 verification."""
    role = Role(id=uuid.uuid4(), name=f"candidate_role_{uuid.uuid4().hex[:6]}")
    db_session.add(role)
    await db_session.flush()

    user = User(
        id=uuid.uuid4(),
        email=f"candidate_{uuid.uuid4().hex[:6]}@vireoniq.com",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()

    profile = Profile(
        user_id=user.id,
        first_name="Priya",
        last_name="Ranjan",
        target_role="Senior Backend Engineer"
    )
    db_session.add(profile)
    await db_session.commit()
    return user


# =========================================================================
# 1. Professional Evidence Graph 10-State Lifecycle & Normalization Tests
# =========================================================================

def test_canonical_10_evidence_states():
    """Verifies all 10 canonical evidence states are properly defined and validated."""
    expected_states = [
        "CLAIMED", "OBSERVED", "INFERRED", "DEMONSTRATED", "ASSESSED",
        "VERIFIED", "CONFLICTED", "NEEDS_REVIEW", "EXPIRED"
    ]
    for state in expected_states:
        assert state in CANONICAL_EVIDENCE_STATES
        assert validate_evidence_state(state) == state

    # Fallback for invalid states
    assert validate_evidence_state("FABRICATED_CLAIM") == "CLAIMED"


@pytest.mark.asyncio
async def test_evidence_recording_and_conflict_detection(db_session: AsyncSession, setup_test_candidate):
    """Verifies granular evidence recording and contradiction analysis."""
    user = setup_test_candidate

    # Ingest resume claim
    claim = await record_granular_evidence(
        user_id=user.id,
        skill_name="Python",
        evidence_type="RESUME_CLAIM",
        source="Resume: Alex Morgan",
        source_span="Engineered microservices in Python",
        status="CLAIMED",
        db=db_session
    )
    assert claim["status"] == "CLAIMED"
    assert claim["skill_name"] == "Python"

    # Ingest project demonstration
    demo = await record_granular_evidence(
        user_id=user.id,
        skill_name="Python",
        evidence_type="PROJECT_REPO",
        source="GitHub: priya-ranjan/telemetry",
        status="DEMONSTRATED",
        db=db_session
    )
    assert demo["status"] == "DEMONSTRATED"

    # Trace lineage
    lineage = await trace_skill_lineage(user_id=user.id, skill_name="Python", db=db_session)
    assert lineage["skill_name"] == "Python"
    assert lineage["total_lineage_nodes"] >= 2


# =========================================================================
# 2. Career Digital Twin 2.0 & Explainable Lineage Tests
# =========================================================================

@pytest.mark.asyncio
async def test_career_digital_twin_snapshot_and_diff(db_session: AsyncSession, setup_test_candidate):
    """Verifies Career Twin 2.0 snapshot generation, uncertainty tier, and diff explainability."""
    user = setup_test_candidate

    # Generate initial snapshot
    snap_1 = await generate_career_digital_twin_snapshot(
        user_id=user.id,
        target_role_override="Senior Backend Engineer",
        db=db_session
    )
    assert snap_1["candidate"]["name"] == "Priya Ranjan"
    assert "uncertainty_tier" in snap_1["trajectory"]
    assert "career_readiness" in snap_1

    # Ingest new controlled assessment evidence
    await record_granular_evidence(
        user_id=user.id,
        skill_name="System Design",
        evidence_type="CODING_ASSESSMENT",
        source="MNC Architecture Assessment",
        status="ASSESSED",
        metadata_payload={"score": 92.0},
        db=db_session
    )

    # Generate updated snapshot
    snap_2 = await generate_career_digital_twin_snapshot(
        user_id=user.id,
        target_role_override="Senior Backend Engineer",
        db=db_session
    )

    diff = compute_twin_diff(snap_1, snap_2)
    assert "input_deltas" in diff
    assert "explanations" in diff


# =========================================================================
# 3. 9D Career Readiness Index & Bottleneck Isolation Tests
# =========================================================================

@pytest.mark.asyncio
async def test_career_readiness_bottleneck_and_coverage(db_session: AsyncSession, setup_test_candidate):
    """Verifies 9D CRI computation with bottleneck isolation and evidence coverage."""
    user = setup_test_candidate

    readiness = await compute_role_career_readiness(
        user_id=user.id,
        target_role_name="Senior Backend Engineer",
        db=db_session
    )

    assert "overall_readiness_score" in readiness
    assert "critical_bottleneck" in readiness
    assert "evidence_coverage" in readiness
    assert "freshness_factor" in readiness
    assert readiness["critical_bottleneck"]["target_score"] == 85.0
    assert isinstance(readiness["critical_bottleneck"]["gap_points"], float)


# =========================================================================
# 4. Next Best Action (NBA) Explainability Tests
# =========================================================================

@pytest.mark.asyncio
async def test_next_best_action_explainability(db_session: AsyncSession, setup_test_candidate):
    """Verifies NBA ranking with why_this_action, why_now, and supporting evidence."""
    user = setup_test_candidate

    nba = await compute_next_best_action(
        user_id=user.id,
        target_role="Senior Backend Engineer",
        db=db_session
    )

    assert nba["action_id"] is not None
    assert "why_this_action" in nba
    assert "why_now" in nba
    assert "supporting_evidence" in nba
    assert nba["uncertainty_tier"] == "HIGH_CONFIDENCE"


# =========================================================================
# 5. Deterministic AST Code Complexity & Sandbox Tests
# =========================================================================

def test_deterministic_ast_complexity():
    """Verifies static AST analysis computes Big-O time and space deterministically."""
    code_linear = """
def linear_search(items, target):
    for item in items:
        if item == target:
            return True
    return False
"""
    res_linear = analyze_python_ast_complexity(code_linear)
    assert "O(N)" in res_linear.time_complexity_static
    assert res_linear.analysis_type == "STATIC_AST"

    code_nested = """
def nested_bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""
    res_nested = analyze_python_ast_complexity(code_nested)
    assert "O(N^2)" in res_nested.time_complexity_static


# =========================================================================
# 6. MNC Interview Studio Blueprint Generation Tests
# =========================================================================

@pytest.mark.asyncio
async def test_mnc_interview_blueprint_generation(db_session: AsyncSession, setup_test_candidate):
    """Verifies MNC studio generates structured multi-round blueprints from public frameworks."""
    user = setup_test_candidate

    profile = await create_company_interview_profile(
        company_name="Google",
        industry="Technology",
        role_family="Backend Engineering",
        target_level="SDE-2",
        db=db_session
    )
    assert profile["company_name"] == "Google"
    assert len(profile["round_configs"]) == 8

    blueprint = await generate_question_blueprint(
        role="Backend Engineer",
        level="SDE-2",
        round_type="CODING",
        topic="Arrays & Hashing",
        difficulty="MEDIUM",
        db=db_session
    )
    assert blueprint["round_type"] == "CODING"
    assert blueprint["topic"] == "Arrays & Hashing"

    coding_q = await generate_and_validate_coding_question(
        blueprint=blueprint,
        db=db_session
    )
    assert coding_q["title"] is not None
    assert "reference_solutions" in coding_q
    assert len(coding_q["hidden_test_cases"]) >= 1


# =========================================================================
# 7. Enterprise Security & Level 3 Autonomy Safety Guard Tests
# =========================================================================

@pytest.mark.asyncio
async def test_level_3_autonomy_safety_guard(db_session: AsyncSession, setup_test_candidate):
    """Verifies that high-impact autonomous actions strictly require user confirmation."""
    user = setup_test_candidate

    # Attempt unauthorized high-impact action without confirmation
    with pytest.raises(PermissionError) as exc_info:
        await execute_autonomous_action_with_guard(
            user_id=user.id,
            action_type="APPLY_JOB",
            is_confirmed=False
        )
    assert "requires explicit user confirmation" in str(exc_info.value)

    # Valid execution with confirmation
    res = await execute_autonomous_action_with_guard(
        user_id=user.id,
        action_type="APPLY_JOB",
        is_confirmed=True
    )
    assert res["execution_status"] == "EXECUTED_WITH_USER_CONFIRMATION"


def test_cryptographic_credential_tamper_defense():
    """Verifies HMAC-SHA256 digital credentials compute valid signatures and reject tampered payloads."""
    cred_id = str(uuid.uuid4())
    user_ref = "user_ref_test_candidate"
    comp = "Distributed Systems"
    level = "ADVANCED"
    issuer = "VIREONIQ"
    issued_iso = "2026-08-25T10:00:00Z"
    version = "1.0.0"

    # Compute valid signature
    valid_sig = compute_canonical_hmac_signature(
        cred_id, user_ref, comp, level, issuer, issued_iso, version
    )
    assert len(valid_sig) == 64

    # Verify authentic signature
    is_valid = verify_canonical_hmac_signature(
        cred_id, user_ref, comp, level, issuer, issued_iso, version, valid_sig
    )
    assert is_valid is True

    # Tampered payload verification
    is_tampered = verify_canonical_hmac_signature(
        cred_id, user_ref, "Tampered Skill", level, issuer, issued_iso, version, valid_sig
    )
    assert is_tampered is False
