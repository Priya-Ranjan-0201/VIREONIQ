import pytest
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from services.skill_intelligence_service import (
    calculate_freshness, sync_skills_from_resume,
    record_assessment_skill_evidence, get_candidate_skill_profile
)
from db.models import SkillEvidence

def test_evidence_freshness_decay_math():
    now = datetime.now(timezone.utc)
    
    # 0 days old -> 100% freshness
    fresh_0 = calculate_freshness(now)
    assert fresh_0 == 100.0

    # 6 months old (~180 days) -> ~78% freshness
    date_6_months = now - timedelta(days=180)
    fresh_6m = calculate_freshness(date_6_months)
    assert 70.0 <= fresh_6m <= 85.0

    # 2 years old (~730 days) -> ~38% freshness
    date_2_years = now - timedelta(days=730)
    fresh_2y = calculate_freshness(date_2_years)
    assert 25.0 <= fresh_2y <= 50.0

@pytest.mark.asyncio
async def test_sync_skills_from_resume_hierarchy(db_session: AsyncSession, test_user):
    parsed_resume = {
        "skills": ["Python", "FastAPI", "Docker", "GraphQL"],
        "projects": [
            {"title": "FastAPI E-commerce Backend", "description": "Built scalable REST API with FastAPI and Python."}
        ]
    }
    
    synced = await sync_skills_from_resume(test_user.id, parsed_resume, db_session)
    assert synced == 4

    profile = await get_candidate_skill_profile(test_user.id, db_session)
    assert len(profile) == 4
    
    skill_dict = {s["skill_name"]: s for s in profile}
    # Python & FastAPI mentioned in projects -> INFERRED tier
    assert skill_dict["Python"]["evidence_tier"] == "INFERRED"
    assert skill_dict["FastAPI"]["evidence_tier"] == "INFERRED"
    # Docker not in project text -> CLAIMED tier
    assert skill_dict["Docker"]["evidence_tier"] == "CLAIMED"

@pytest.mark.asyncio
async def test_skill_elevation_after_assessment(db_session: AsyncSession, test_user):
    record = await record_assessment_skill_evidence(
        user_id=test_user.id,
        skill_name="Python",
        assessment_title="LRU Cache & Concurrency Sandbox",
        score=92.0,
        runtime_complexity="O(1)",
        integrity_score=98.0,
        db=db_session
    )
    
    assert record.skill_name == "Python"
    assert record.evidence_tier == "VERIFIED"
    assert float(record.score) == 92.0
    assert record.confidence == "HIGH"
    assert "LRU Cache" in record.explanation
