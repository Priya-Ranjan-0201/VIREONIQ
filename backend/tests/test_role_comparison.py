import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from services.role_comparison_service import compute_candidate_role_alignment, compare_roles
from services.skill_intelligence_service import record_assessment_skill_evidence

@pytest.mark.asyncio
async def test_candidate_role_alignment_classifications(db_session: AsyncSession, test_user):
    # Establish Python as assessed
    await record_assessment_skill_evidence(
        user_id=test_user.id,
        skill_name="Python",
        assessment_title="Core Assessment",
        score=95.0,
        runtime_complexity="O(1)",
        integrity_score=98.0,
        db=db_session
    )

    alignment = await compute_candidate_role_alignment(test_user.id, "Backend Engineer", db_session)

    assert "overall_alignment_percentage" in alignment
    assert "summary" in alignment
    
    # Verify Python is MATCHED
    matched_skills = [m["skill_name"] for m in alignment["matched_competencies"]]
    assert "Python" in matched_skills

    # Verify unassessed/unclaimed role skills are classified as UNKNOWN (Insufficient Evidence)
    unknown_skills = [u["skill_name"] for u in alignment["unknown_competencies"]]
    assert len(unknown_skills) >= 1
    # Check that UNKNOWN status explicitly states insufficient evidence
    first_unknown = alignment["unknown_competencies"][0]
    assert first_unknown["status"] == "UNKNOWN"
    assert "insufficient evidence" in first_unknown["reasoning"].lower()

@pytest.mark.asyncio
async def test_multi_role_comparison(db_session: AsyncSession, test_user):
    comp = await compare_roles(test_user.id, "Backend Engineer", "AI/ML Engineer", db_session)

    assert "role_a" in comp
    assert "role_b" in comp
    assert "comparison_metrics" in comp
    
    metrics = comp["comparison_metrics"]
    assert "Python" in metrics["shared_competencies"]
    assert len(metrics["unique_to_role_a"]) >= 1 # e.g. PostgreSQL, System Design
    assert len(metrics["unique_to_role_b"]) >= 1 # e.g. PyTorch, Machine Learning
