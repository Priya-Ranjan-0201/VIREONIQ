import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import SkillEvidence, EvidenceItem, AssessmentEvaluationResult
from services.unified_assessment_service import (
    create_assessment_session, get_next_adaptive_question,
    submit_question_response, finalize_assessment_session
)
from services.career_digital_twin_service import generate_career_digital_twin_snapshot

@pytest.mark.asyncio
async def test_section_63_closed_loop_career_assessment(db_session: AsyncSession, test_user):
    """
    Executes the full Section 63 Closed Assessment Loop:
      1. Candidate starts Backend Engineer assessment
      2. Adaptive questions are served and evaluated
      3. Assessment is finalized
      4. EvidenceItems and SkillEvidence (ASSESSED) are generated
      5. Career Digital Twin is updated
      6. Readiness and Next Best Action are refreshed
    """
    # 1. Start Assessment
    session_data = await create_assessment_session(
        user_id=test_user.id,
        target_role="Backend Engineer",
        mode="ASSESSMENT",
        db=db_session
    )
    session_id = uuid.UUID(session_data["session_id"])

    # 2. Answer Question 1 (Python)
    q1 = await get_next_adaptive_question(session_id, db_session)
    valid_code = "def two_sum_indexed(nums, target):\n    lookup = {}\n    for i, n in enumerate(nums):\n        if target - n in lookup: return [lookup[target-n], i]\n        lookup[n] = i\n    return []\n"
    await submit_question_response(
        session_id=session_id,
        question_id=uuid.UUID(q1["question_id"]),
        response_data={"code_submission": valid_code, "duration_seconds": 45.0},
        db=db_session
    )

    # 3. Finalize Assessment Session
    final_res = await finalize_assessment_session(session_id, db_session)

    assert "evidence_created_count" in final_res
    assert final_res["evidence_created_count"] >= 4
    assert "recalculated_career_readiness" in final_res
    assert final_res["recalculated_career_readiness"] > 0
    assert "highest_roi_next_action" in final_res

    # 4. Verify EvidenceItems generated in Database
    ev_items = (await db_session.execute(
        select(EvidenceItem).where(EvidenceItem.user_id == test_user.id)
    )).scalars().all()
    assert len(ev_items) >= 4
    assert any(e.status == "ASSESSED" for e in ev_items)

    # 5. Verify SkillEvidence elevated to ASSESSED
    skills = (await db_session.execute(
        select(SkillEvidence).where(SkillEvidence.user_id == test_user.id)
    )).scalars().all()
    assert len(skills) >= 4
    assert any(s.evidence_tier == "ASSESSED" for s in skills)

    # 6. Verify Career Digital Twin Snapshot reflects newly verified assessments
    twin_snapshot = await generate_career_digital_twin_snapshot(test_user.id, "Backend Engineer", db_session)
    assert twin_snapshot["skills_inventory"]["verified_count"] >= 4
    assert twin_snapshot["career_readiness"]["overall_score"] == final_res["recalculated_career_readiness"]
