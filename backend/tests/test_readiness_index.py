import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from services.readiness_index_service import compute_career_readiness_index
from services.skill_intelligence_service import record_assessment_skill_evidence

@pytest.mark.asyncio
async def test_compute_career_readiness_index_dimensions(db_session: AsyncSession, test_user):
    # Add verified skills
    await record_assessment_skill_evidence(
        user_id=test_user.id,
        skill_name="Python",
        assessment_title="Backend Concurrency",
        score=88.0,
        runtime_complexity="O(N)",
        integrity_score=95.0,
        db=db_session
    )
    
    cri_data = await compute_career_readiness_index(test_user.id, "Backend Engineer", db_session)
    
    assert cri_data["target_role"] == "Backend Engineer"
    assert 0.0 <= cri_data["overall_readiness"] <= 100.0
    
    dims = cri_data["dimensions"]
    assert len(dims) == 8
    
    # Verify all 8 dimensions are present with explainability attributes
    for dim_key in [
        "technical_capability", "project_capability", "coding_mastery", "system_design",
        "communication_score", "interview_readiness", "resume_evidence_strength", "role_alignment"
    ]:
        assert dim_key in dims
        dim = dims[dim_key]
        assert "score" in dim
        assert "why" in dim
        assert "evidence" in dim
        assert "confidence" in dim
        assert "next_action" in dim
        assert isinstance(dim["evidence"], list)
