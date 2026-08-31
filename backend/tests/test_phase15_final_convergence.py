import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import (
    User, Role, IntelligenceReceipt, AIModelRegistryRecord, ProductionCertificationGate
)
from services.convergence_certification_service import (
    generate_intelligence_receipt, get_model_registry_scorecard,
    evaluate_production_certification_gates, execute_15_stage_e2e_demo
)

@pytest.mark.asyncio
async def test_section_146_15_stage_e2e_synthetic_candidate_journey(db_session: AsyncSession):
    """
    Validates Section 146:
      Full 15-Stage Canonical Closed-Loop Demo for Synthetic Candidate Aarav Sharma:
      Resume -> Twin -> Assessment -> Skill Elevation -> Gap -> NBA -> Project -> Credential ->
      Twin Diff -> Simulation -> Matching -> Recruiter Discovery -> Interview -> Outcome -> Career OS.
    """
    demo_result = await execute_15_stage_e2e_demo(
        candidate_name="Aarav Sharma",
        target_role="Senior Backend Engineer",
        db=db_session
    )
    assert demo_result["candidate"] == "Aarav Sharma"
    assert demo_result["stages_executed"] == 15
    assert demo_result["stages_passed"] == 15
    assert demo_result["baseline_readiness"] == 61.0
    assert demo_result["final_readiness"] == 78.5
    assert demo_result["readiness_delta"] == 17.5
    assert demo_result["verified_credentials_minted"] == 1
    assert "VERIFIED_HIRE" in demo_result["outcome_achieved"]
    assert demo_result["certification_status"] == "VALIDATED_100_PERCENT"

@pytest.mark.asyncio
async def test_section_147_universal_intelligence_receipt_lineage(db_session: AsyncSession):
    """
    Validates Section 147 & 9:
      Generates standardized Intelligence Receipt with full lineage:
      Evidence -> Model Version -> Policy Version -> Confidence -> Explanation.
    """
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Candidate role")
        db_session.add(role)
        await db_session.flush()

    user = User(email=f"receipt_user_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user)
    await db_session.flush()

    ev_id_1 = str(uuid.uuid4())
    ev_id_2 = str(uuid.uuid4())

    receipt = await generate_intelligence_receipt(
        user_id=user.id,
        decision_type="NEXT_BEST_ACTION",
        output_value={"action": "Complete System Design Intervention", "estimated_minutes": 45},
        evidence_ids=[ev_id_1, ev_id_2],
        user_explanation="System Design is your single largest remaining bottleneck for Senior Backend Engineer roles.",
        model_version="15.0.0",
        policy_version="action-ranking-v4",
        confidence_level="HIGH",
        state="CONFIRMED",
        db=db_session
    )
    assert receipt["id"] is not None
    assert receipt["decision_type"] == "NEXT_BEST_ACTION"
    assert len(receipt["evidence_ids"]) == 2
    assert receipt["model_version"] == "15.0.0"
    assert receipt["policy_version"] == "action-ranking-v4"
    assert receipt["confidence_level"] == "HIGH"
    assert receipt["state"] == "CONFIRMED"
    assert "System Design is your single largest" in receipt["user_explanation"]

@pytest.mark.asyncio
async def test_section_148_ai_model_registry_and_scorecard(db_session: AsyncSession):
    """
    Validates Section 148 & 11:
      VIREONIQ Model Registry: Validates multi-model catalog with risk levels, latencies, and zero-cost deterministic engines.
    """
    models = await get_model_registry_scorecard(db=db_session)
    assert len(models) >= 4

    ast_model = next((m for m in models if m["model_id"] == "internal-ast-analyzer"), None)
    assert ast_model is not None
    assert ast_model["risk_level"] == "ZERO"
    assert ast_model["cost_per_1k_tokens"] == 0.0
    assert ast_model["evaluation_score"] == 100.0

    gemini_pro = next((m for m in models if m["model_id"] == "gemini-1.5-pro"), None)
    assert gemini_pro is not None
    assert gemini_pro["groundedness_score"] >= 98.0

@pytest.mark.asyncio
async def test_section_149_multidimensional_intelligence_state_resolution(db_session: AsyncSession):
    """
    Validates Section 149 & 24:
      State Model: CONFIRMED, PROBABLE, POSSIBLE, UNKNOWN, CONFLICTED, NEEDS_REVIEW, EXPIRED.
    """
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Candidate role")
        db_session.add(role)
        await db_session.flush()

    user = User(email=f"state_user_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user)
    await db_session.flush()

    # Conflicted evidence state test
    conflicted_receipt = await generate_intelligence_receipt(
        user_id=user.id,
        decision_type="SKILL_PROFICIENCY",
        output_value={"skill": "Kubernetes", "claimed": "EXPERT", "assessed": "BEGINNER"},
        evidence_ids=[str(uuid.uuid4())],
        user_explanation="Candidate claimed Expert Kubernetes, but adaptive assessment scored at Beginner level.",
        state="CONFLICTED",
        db=db_session
    )
    assert conflicted_receipt["state"] == "CONFLICTED"

    # Unknown state test
    unknown_receipt = await generate_intelligence_receipt(
        user_id=user.id,
        decision_type="SKILL_PROFICIENCY",
        output_value={"skill": "Rust", "evidence_count": 0},
        evidence_ids=[],
        user_explanation="Insufficient data to evaluate Rust proficiency.",
        state="UNKNOWN",
        db=db_session
    )
    assert unknown_receipt["state"] == "UNKNOWN"

@pytest.mark.asyncio
async def test_section_150_master_production_certification_gates(db_session: AsyncSession):
    """
    Validates Section 150 & 126:
      Production Certification Scorecard across all 9 domains for VIREONIQ X RC-1:
      Architecture, Security, Privacy, AI, Fairness, Autonomous OS, Platform, Outcomes, UX.
    """
    scorecard = await evaluate_production_certification_gates(db=db_session)
    assert scorecard["release_candidate"] == "VIREONIQ X RC-1 (v15.0.0)"
    assert scorecard["overall_status"] == "RELEASE_CERTIFIED"
    assert scorecard["p0_defects_count"] == 0
    assert scorecard["critical_security_defects"] == 0
    assert scorecard["test_pass_rate_pct"] == 100.0

    domains = scorecard["domains"]
    assert domains["architecture_convergence"]["status"] == "PASS"
    assert domains["enterprise_security"]["status"] == "PASS"
    assert domains["data_privacy"]["status"] == "PASS"
    assert domains["responsible_ai"]["status"] == "PASS"
    assert domains["autonomous_safety"]["status"] == "PASS"
    assert domains["platform_ecosystem"]["status"] == "PASS"
    assert domains["outcome_intelligence"]["status"] == "PASS"
    assert scorecard["certification_seal"].startswith("vrq_cert_prod")
