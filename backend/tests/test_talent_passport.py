import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from services.credential_service import get_talent_passport_data
from services.skill_intelligence_service import record_assessment_skill_evidence

@pytest.mark.asyncio
async def test_dynamic_talent_passport(db_session: AsyncSession, test_user):
    # Add assessed skills
    await record_assessment_skill_evidence(
        user_id=test_user.id,
        skill_name="Python",
        assessment_title="Backend Architecture Challenge",
        score=94.0,
        runtime_complexity="O(1)",
        integrity_score=98.0,
        db=db_session
    )

    passport = await get_talent_passport_data(test_user.id, db_session)
    
    assert "passport_id" in passport
    assert "tier" in passport
    assert "overall_readiness_score" in passport
    assert "verification_status" in passport
    assert "evidence_freshness_factor" in passport
    assert passport["evidence_freshness_factor"] > 0
    assert "verified_competencies" in passport
    assert len(passport["verified_competencies"]) >= 1
    assert "public_verification_url" in passport
