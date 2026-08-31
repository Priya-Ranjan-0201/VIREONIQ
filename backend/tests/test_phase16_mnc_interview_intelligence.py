import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import (
    User, Role, MNCCompanyInterviewProfile, MNCQuestionBlueprint,
    MNCCodingQuestion, MNCInterviewSession, MNCInterviewTurn,
    SkillEvidence, IntelligenceReceipt
)
from services.mnc_interview_intelligence_service import (
    create_company_interview_profile, generate_question_blueprint,
    generate_and_validate_coding_question, start_mnc_interview_session,
    process_interview_turn_and_follow_up, evaluate_code_submission_deterministic,
    finalize_mnc_interview_and_sync_twin
)

@pytest.mark.asyncio
async def test_section_151_company_interview_profile_and_rounds(db_session: AsyncSession):
    """
    Validates Section 151:
      Configurable MNC company interview profiles with 8 distinct rounds and skill weighting.
    """
    profile = await create_company_interview_profile(
        company_name="Google",
        industry="Technology",
        role_family="Backend Engineering",
        target_level="SDE-2",
        db=db_session
    )
    assert profile["company_name"] == "Google"
    assert len(profile["round_configs"]) == 8
    assert profile["skill_weights"]["DSA"] == 0.35
    assert profile["source_policy"] == "PUBLICLY_REPORTED"

@pytest.mark.asyncio
async def test_section_152_question_blueprint_and_coding_generation(db_session: AsyncSession):
    """
    Validates Section 152:
      Generates structured blueprint and validates coding question with hidden test cases and complexity constraints.
    """
    blueprint = await generate_question_blueprint(
        role="Backend Engineer",
        level="SDE-2",
        round_type="CODING",
        topic="Arrays & Hashing",
        difficulty="MEDIUM",
        db=db_session
    )
    assert blueprint["topic"] == "Arrays & Hashing"
    assert blueprint["difficulty"] == "MEDIUM"
    assert blueprint["expected_time_minutes"] == 35

    coding_q = await generate_and_validate_coding_question(
        blueprint=blueprint,
        language="python",
        db=db_session
    )
    assert coding_q["title"] is not None
    assert len(coding_q["public_test_cases"]) >= 1
    assert len(coding_q["hidden_test_cases"]) >= 1
    assert coding_q["expected_time_complexity"] == "O(N)"
    assert coding_q["validation_status"] == "APPROVED"

@pytest.mark.asyncio
async def test_section_153_reference_solution_quality_gate(db_session: AsyncSession):
    """
    Validates Section 153:
      Reference solution passes AST syntax and quality gate before question is marked APPROVED.
    """
    blueprint = await generate_question_blueprint(
        role="Backend Engineer",
        level="Senior",
        round_type="CODING",
        topic="System Oriented",
        difficulty="HARD",
        db=db_session
    )
    coding_q = await generate_and_validate_coding_question(
        blueprint=blueprint,
        language="python",
        db=db_session
    )
    assert coding_q["validation_status"] == "APPROVED"
    assert "LRUCache" in coding_q["reference_solutions"]["python"]

@pytest.mark.asyncio
async def test_section_154_dynamic_follow_up_branching(db_session: AsyncSession):
    """
    Validates Section 154:
      Conversational interview branching: generates targeted follow-up based on candidate's architectural claims.
    """
    session_id = uuid.uuid4()
    turn = await process_interview_turn_and_follow_up(
        session_id=session_id,
        question_text="How do you handle heavy read workloads on user profile queries?",
        candidate_response="We used a distributed Redis cache in front of PostgreSQL.",
        question_category="SYSTEM_DESIGN",
        turn_number=1,
        db=db_session
    )
    assert turn["follow_up_prompt"] is not None
    assert "invalidation" in turn["follow_up_prompt"].lower() or "cache" in turn["follow_up_prompt"].lower()
    assert turn["evaluation_scores"]["technical_depth"] >= 90.0

@pytest.mark.asyncio
async def test_section_155_deterministic_ast_code_evaluation():
    """
    Validates Section 155:
      Deterministic evaluation: verifies test cases and AST Big-O runtime complexity.
    """
    dummy_q = {
        "title": "Subarray Sum",
        "public_test_cases": [1, 2],
        "hidden_test_cases": [3, 4],
        "expected_time_complexity": "O(N)"
    }
    user_code = """
def solve(nums, k):
    count = 0
    for n in nums:
        count += n
    return count
"""
    eval_result = evaluate_code_submission_deterministic(
        question=dummy_q,
        code_submission=user_code,
        language="python"
    )
    assert eval_result["is_passed"] is True
    assert eval_result["evaluated_complexity"] == "O(N)"
    assert eval_result["public_tests_passed"] == 2
    assert eval_result["hidden_tests_passed"] == 2
    assert eval_result["score"] >= 90.0

@pytest.mark.asyncio
async def test_section_156_closed_loop_mnc_assessment_sync(db_session: AsyncSession):
    """
    Validates Section 156:
      Closed loop: Finalizes MNC interview session -> Elevates skill evidence to ASSESSED ->
      Updates Career Twin -> Mints Intelligence Receipt.
    """
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Candidate role")
        db_session.add(role)
        await db_session.flush()

    user = User(email=f"mnc_candidate_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user)
    await db_session.flush()

    session = await start_mnc_interview_session(
        user_id=user.id,
        target_company="Google",
        target_role="Senior Backend Engineer",
        target_level="SDE-2",
        mode="ASSESSMENT",
        db=db_session
    )
    session_id = uuid.UUID(session["id"])

    final_summary = await finalize_mnc_interview_and_sync_twin(
        session_id=session_id,
        user_id=user.id,
        target_role="Senior Backend Engineer",
        db=db_session
    )
    assert final_summary["status"] == "COMPLETED"
    assert final_summary["overall_score"] >= 90.0
    assert final_summary["evidence_tier_elevated"] == "ASSESSED"
    assert final_summary["receipt_id"] is not None

    # Verify SkillEvidence record in DB
    ev_stmt = select(SkillEvidence).where(SkillEvidence.user_id == user.id)
    ev_records = (await db_session.execute(ev_stmt)).scalars().all()
    assert len(ev_records) >= 1
    assert any(e.evidence_tier == "ASSESSED" for e in ev_records)
