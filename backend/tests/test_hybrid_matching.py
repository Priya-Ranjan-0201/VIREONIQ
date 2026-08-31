import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from services.hybrid_matching_service import compute_explainable_match
from services.skill_intelligence_service import record_assessment_skill_evidence

@pytest.mark.asyncio
async def test_hybrid_matching_breakdown(db_session: AsyncSession, test_user):
    # Add skills
    await record_assessment_skill_evidence(
        user_id=test_user.id,
        skill_name="Python",
        assessment_title="Algorithm Optimization",
        score=90.0,
        runtime_complexity="O(N)",
        integrity_score=95.0,
        db=db_session
    )
    await record_assessment_skill_evidence(
        user_id=test_user.id,
        skill_name="PostgreSQL",
        assessment_title="Database Indexing",
        score=85.0,
        runtime_complexity="O(log N)",
        integrity_score=90.0,
        db=db_session
    )

    match_result = await compute_explainable_match(
        user_id=test_user.id,
        job_id=None,
        target_role_name="Backend Engineer",
        db=db_session
    )

    assert 0.0 <= match_result["overall_match_percentage"] <= 100.0
    assert "dimension_breakdown" in match_result
    assert "matched_competencies" in match_result
    assert "missing_competencies" in match_result
    assert "explanation" in match_result

    matched_names = [m["name"] for m in match_result["matched_competencies"]]
    assert "Python" in matched_names
    assert "PostgreSQL" in matched_names
