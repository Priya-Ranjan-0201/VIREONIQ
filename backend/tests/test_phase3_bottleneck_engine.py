import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from services.career_bottleneck_engine import identify_career_bottlenecks
from services.skill_intelligence_service import record_assessment_skill_evidence, sync_skills_from_resume

@pytest.mark.asyncio
async def test_material_bottleneck_detection_vs_lowest_score(db_session: AsyncSession, test_user):
    """
    Validates that a low score in a high-importance dependency skill (e.g. System Design)
    is identified as the primary bottleneck over an optional/low-importance skill.
    """
    # High Python
    await record_assessment_skill_evidence(
        user_id=test_user.id,
        skill_name="Python",
        assessment_title="Python Advanced",
        score=95.0,
        runtime_complexity="O(1)",
        integrity_score=98.0,
        db=db_session
    )

    # Moderate/Claimed System Design (Importance: 90)
    await sync_skills_from_resume(
        user_id=test_user.id,
        parsed_resume={"skills": ["Python", "System Design"]},
        db=db_session
    )

    bottlenecks = await identify_career_bottlenecks(test_user.id, "Backend Engineer", db_session)

    assert bottlenecks["has_bottleneck"] is True
    primary = bottlenecks["primary_bottleneck"]
    assert primary is not None
    assert "System Design" in primary["skill_name"] or primary["role_importance"] >= 80
    assert "diagnosis" in primary
    assert len(bottlenecks["all_constraints_ranked"]) >= 1
