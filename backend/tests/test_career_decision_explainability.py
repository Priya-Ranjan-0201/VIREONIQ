import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

from main import app
from db.models import Base, Role, User, Profile, SkillEvidence
from db.session import get_db
from core.security import create_access_token
from services.career_decision_explainability_service import (
    build_decision_explanation, generate_explainable_career_recommendation, explain_what_if_simulation
)
from services.career_intervention_engine import generate_next_best_actions
from services.evidence_graph_service import record_granular_evidence


@pytest.fixture
async def test_db():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session
    
    await engine.dispose()


async def create_test_user(db: AsyncSession, email: str = "explainability_test@vireoniq.com") -> User:
    role_id = uuid.uuid4()
    role = Role(id=role_id, name=f"Candidate_{uuid.uuid4().hex[:6]}")
    db.add(role)
    await db.flush()

    user_id = uuid.uuid4()
    user = User(id=user_id, email=email, role_id=role_id, is_active=True)
    db.add(user)
    await db.flush()
    return user


@pytest.mark.asyncio
async def test_decision_explanation_structure_and_no_false_precision():
    """
    Verifies that decision explanations strictly adhere to the required schema
    and avoid false precision (using ranges instead of single floating points).
    """
    explanation = build_decision_explanation(
        recommendation="Complete System Design Assessment",
        reason="Python backend capability demonstrated, but system design is a critical role requirement.",
        supporting_evidence=[{"skill": "Python", "score": 85.0, "tier": "DEMONSTRATED"}],
        identified_gap={"skill": "System Design", "current_score": 61.0, "target": 80.0},
        role_requirement={"target_role": "Backend Engineer", "importance": "HIGH", "weight": 0.85},
        market_signal={"demand_trend": "HIGH", "priority": "P1"},
        expected_impact_range="+6 to +10 pts on 9D Career Readiness",
        estimated_effort_range="12–18 hours",
        confidence="MEDIUM",
        assumptions=["Consistent 8–10 hrs/week study schedule."],
        alternatives=[{"title": "Cloud Architecture Assessment", "type": "LAB_CHECK"}],
        limitations=["Subject to proctored verification."]
    )

    assert "recommendation" in explanation
    assert "reason" in explanation
    assert "supporting_evidence" in explanation
    assert "identified_gap" in explanation
    assert "role_requirement" in explanation
    assert "market_signal" in explanation
    assert "expected_impact" in explanation
    assert "estimated_effort" in explanation
    assert "confidence" in explanation
    assert "assumptions" in explanation
    assert "alternatives" in explanation
    assert "limitations" in explanation
    assert "timestamp" in explanation
    assert "policy_version" in explanation

    # Verify no false precision
    assert "to" in explanation["expected_impact"]
    assert "hours" in explanation["estimated_effort"]
    assert explanation["confidence"] == "MEDIUM"


@pytest.mark.asyncio
async def test_explainable_recommendation_with_evidence_conflicts(test_db):
    """
    Verifies explanation generation when candidate has active evidence contradiction.
    """
    user = await create_test_user(test_db, "conflict_explain@vireoniq.com")
    
    await record_granular_evidence(user.id, "Python", "RESUME_CLAIM", "Resume", status="CLAIMED", db=test_db)
    await record_granular_evidence(user.id, "Python", "CODING_ASSESSMENT", "Test", status="ASSESSED", metadata_payload={"score": 45.0}, db=test_db)

    exp = await generate_explainable_career_recommendation(user.id, "Backend Engineer", db=test_db)
    assert "Resolve Python Evidence Contradiction" in exp["recommendation"]
    assert exp["confidence"] == "HIGH"
    assert len(exp["alternatives"]) >= 1
    assert "Evidence Integrity" in exp["expected_impact"]


@pytest.mark.asyncio
async def test_explainable_recommendation_with_prerequisite_bottleneck(test_db):
    """
    Verifies explanation generation when candidate has an ungrounded prerequisite.
    """
    user = await create_test_user(test_db, "prereq_explain@vireoniq.com")
    
    # Candidate knows Python (85) and FastAPI (75) but missing HTTP & Networking (<65)
    s1 = SkillEvidence(id=uuid.uuid4(), user_id=user.id, skill_name="Python", score=85.0, evidence_tier="ASSESSED")
    s2 = SkillEvidence(id=uuid.uuid4(), user_id=user.id, skill_name="HTTP & Networking", score=42.0, evidence_tier="CLAIMED")
    test_db.add_all([s1, s2])
    await test_db.flush()

    exp = await generate_explainable_career_recommendation(user.id, "REST APIs", db=test_db)
    assert "Http & Networking" in exp["recommendation"] or "HTTP & Networking" in exp["recommendation"]
    assert "prerequisite" in exp["reason"].lower() or "foundational" in exp["reason"].lower()


@pytest.mark.asyncio
async def test_nba_decision_explanation_integration(test_db):
    """
    Verifies that Next Best Actions automatically include structured decision explanations.
    """
    user = await create_test_user(test_db, "nba_explain@vireoniq.com")
    
    nbas = await generate_next_best_actions(user.id, "Backend Engineer", test_db)
    assert len(nbas) > 0
    for nba in nbas:
        assert "decision_explanation" in nba
        exp = nba["decision_explanation"]
        assert "recommendation" in exp
        assert "reason" in exp
        assert "expected_impact" in exp
        assert "confidence" in exp


@pytest.mark.asyncio
async def test_explainable_recommendations_endpoint(test_db):
    """
    Verifies the HTTP endpoint GET /api/v1/interventions/explainable-recommendations.
    """
    user = await create_test_user(test_db, "endpoint_explain@vireoniq.com")

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    token = create_access_token(subject=str(user.id), jti=f"exp_{uuid.uuid4().hex[:8]}")
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/interventions/explainable-recommendations?target_role=Backend%20Engineer", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "recommendation" in data
        assert "reason" in data
        assert "expected_impact" in data
        assert "confidence" in data
        assert "assumptions" in data
        assert "alternatives" in data
        assert "limitations" in data

    app.dependency_overrides.clear()
