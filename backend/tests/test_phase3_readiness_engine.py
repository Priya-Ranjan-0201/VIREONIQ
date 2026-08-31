import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from services.career_readiness_engine import compute_role_career_readiness
from services.skill_intelligence_service import record_assessment_skill_evidence, sync_skills_from_resume

@pytest.mark.asyncio
async def test_role_specific_career_readiness_scoring(db_session: AsyncSession, test_user):
    # Setup candidate with Backend-centric evidence
    await record_assessment_skill_evidence(
        user_id=test_user.id,
        skill_name="Python",
        assessment_title="Core Assessment",
        score=92.0,
        runtime_complexity="O(N)",
        integrity_score=98.0,
        db=db_session
    )

    await sync_skills_from_resume(
        user_id=test_user.id,
        parsed_resume={"skills": ["Python", "FastAPI", "PostgreSQL", "REST APIs", "SQL"]},
        db=db_session
    )

    # Compute readiness for Backend Engineer
    backend_res = await compute_role_career_readiness(test_user.id, "Backend Engineer", db_session)
    
    # Compute readiness for AI/ML Engineer (which requires PyTorch, ML, Math)
    aiml_res = await compute_role_career_readiness(test_user.id, "AI/ML Engineer", db_session)

    # Backend readiness must be different and higher than AI/ML readiness
    assert backend_res["overall_readiness_score"] > 0
    assert aiml_res["overall_readiness_score"] > 0
    assert backend_res["overall_readiness_score"] >= aiml_res["overall_readiness_score"]

    # Verify metadata versioning
    assert backend_res["metadata"]["readiness_model_version"] == "v3.0.0"
    assert "calculated_at" in backend_res["metadata"]

@pytest.mark.asyncio
async def test_dimension_contribution_analysis(db_session: AsyncSession, test_user):
    res = await compute_role_career_readiness(test_user.id, "Backend Engineer", db_session)

    contributions = res["dimension_contributions"]
    assert len(contributions) == 9
    assert "technical_capability" in contributions
    assert "coding_capability" in contributions
    assert "project_capability" in contributions
    assert "system_design" in contributions
    assert "role_alignment" in contributions

    # Check that contribution points are positive and sum to the total weighted score
    total_pts = sum(c["contribution_points"] for c in contributions.values())
    assert abs(total_pts - res["overall_readiness_score"]) <= 1.5

    # Check explainability structure
    expl = res["explanation"]
    assert "summary" in expl
    assert "limiting_constraint" in expl
