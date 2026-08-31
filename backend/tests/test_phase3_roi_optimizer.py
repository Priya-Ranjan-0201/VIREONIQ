import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from services.roi_career_optimizer_service import compute_next_best_career_actions
from services.skill_intelligence_service import record_assessment_skill_evidence, sync_skills_from_resume

@pytest.mark.asyncio
async def test_roi_career_optimizer_ranking_and_previews(db_session: AsyncSession, test_user):
    # Candidate with Python and SQL, missing System Design & Distributed Systems
    await record_assessment_skill_evidence(
        user_id=test_user.id,
        skill_name="Python",
        assessment_title="Core Assessment",
        score=90.0,
        runtime_complexity="O(N)",
        integrity_score=98.0,
        db=db_session
    )
    await sync_skills_from_resume(
        user_id=test_user.id,
        parsed_resume={"skills": ["Python", "FastAPI", "SQL"]},
        db=db_session
    )

    optimizer_res = await compute_next_best_career_actions(test_user.id, "Backend Engineer", db_session)

    assert "highest_roi_action" in optimizer_res
    top_action = optimizer_res["highest_roi_action"]
    assert top_action is not None
    assert "action_id" in top_action
    assert "roi_score" in top_action
    assert "preview" in top_action
    assert "projected_readiness_range" in top_action["preview"]
    assert "why_this_action" in top_action
    assert top_action["multi_gap_closure_count"] >= 1

    # Check that interventions are sorted in descending order of ROI
    interventions = optimizer_res["ranked_interventions"]
    for i in range(len(interventions) - 1):
        assert interventions[i]["roi_score"] >= interventions[i+1]["roi_score"]
