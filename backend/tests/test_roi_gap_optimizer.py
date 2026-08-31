import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from services.roi_gap_optimizer import calculate_roi_gaps
from services.skill_intelligence_service import record_assessment_skill_evidence

@pytest.mark.asyncio
async def test_roi_gap_optimizer_ranking(db_session: AsyncSession, test_user):
    # Establish Python as verified
    await record_assessment_skill_evidence(
        user_id=test_user.id,
        skill_name="Python",
        assessment_title="Core Assessment",
        score=95.0,
        runtime_complexity="O(1)",
        integrity_score=95.0,
        db=db_session
    )

    gaps = await calculate_roi_gaps(test_user.id, "Backend Engineer", db_session)
    assert len(gaps) > 0

    # Ensure prioritized order
    for i in range(len(gaps) - 1):
        assert gaps[i]["priority_score"] >= gaps[i+1]["priority_score"]

    top_gap = gaps[0]
    assert "skill_name" in top_gap
    assert "priority_score" in top_gap
    assert "recommended_action" in top_gap
    assert "recommended_project" in top_gap
    assert "estimated_effort" in top_gap
