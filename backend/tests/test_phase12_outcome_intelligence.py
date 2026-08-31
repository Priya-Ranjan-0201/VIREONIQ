import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import (
    User, Role, Profile, SkillEvidence, VerifiedCredential, CareerInterventionPlan,
    AssessmentResult, AnalyticsEvent, CareerMilestoneProgression
)
from services.outcome_intelligence_service import (
    record_analytics_event, update_candidate_milestone_progression,
    detect_data_quality_anomalies, calculate_career_value_funnel,
    generate_grounded_executive_insights
)

@pytest.mark.asyncio
async def test_section_95_synthetic_candidate_career_funnel(db_session: AsyncSession):
    """
    Validates Section 95:
      Synthetic candidate progression across career value funnel stages.
      Verifies baseline vs current readiness delta calculation.
    """
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Candidate role")
        db_session.add(role)
        await db_session.flush()

    user = User(email=f"funnel_user_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user)
    await db_session.flush()

    # 1. Initialize Milestone Progression (Baseline: 61.0)
    prog_init = await update_candidate_milestone_progression(
        user_id=user.id,
        target_role="Backend Engineer",
        current_readiness=61.0,
        funnel_stage="TWIN_CREATED",
        db=db_session
    )
    assert prog_init["baseline_readiness"] == 61.0
    assert prog_init["readiness_delta"] == 0.0

    # 2. Advance to Verified Readiness (Current: 78.0 -> Delta: +17.0)
    prog_updated = await update_candidate_milestone_progression(
        user_id=user.id,
        target_role="Backend Engineer",
        current_readiness=78.0,
        funnel_stage="VERIFIED_EVIDENCE_READY",
        db=db_session
    )
    assert prog_updated["current_readiness"] == 78.0
    assert prog_updated["readiness_delta"] == 17.0
    assert prog_updated["current_funnel_stage"] == "VERIFIED_EVIDENCE_READY"

@pytest.mark.asyncio
async def test_section_96_analytics_event_idempotency(db_session: AsyncSession):
    """
    Validates Section 96:
      Analytics event ingestion enforces idempotency keys, ignoring duplicate events.
    """
    user_id = uuid.uuid4()
    idem_key = f"evt_idempotent_{uuid.uuid4().hex[:8]}"

    # First event ingestion
    evt1 = await record_analytics_event(
        event_type="ASSESSMENT_COMPLETED",
        actor_id=user_id,
        idempotency_key=idem_key,
        metadata={"score": 88.5},
        db=db_session
    )
    assert evt1["status"] == "RECORDED"

    # Duplicate ingestion with same idempotency key
    evt2 = await record_analytics_event(
        event_type="ASSESSMENT_COMPLETED",
        actor_id=user_id,
        idempotency_key=idem_key,
        metadata={"score": 88.5},
        db=db_session
    )
    assert evt2["status"] == "DUPLICATE_IDEMPOTENT_IGNORED"
    assert evt2["event_id"] == evt1["event_id"]

@pytest.mark.asyncio
async def test_section_97_data_quality_anomaly_detector():
    """
    Validates Section 97:
      Flags unbacked readiness jumps (> +15.0 pts without new evidence) as DATA_QUALITY_ANOMALY.
    """
    # 1. Normal genuine progression (+12.0 pts with 2 new evidence items) -> No anomaly
    clean = detect_data_quality_anomalies(previous_readiness=60.0, new_readiness=72.0, evidence_count_delta=2)
    assert clean is None

    # 2. Suspicious artificial spike (+25.0 pts with 0 new evidence items) -> Anomaly detected
    anomaly = detect_data_quality_anomalies(previous_readiness=60.0, new_readiness=85.0, evidence_count_delta=0)
    assert anomaly is not None
    assert anomaly["anomaly_type"] == "UNGROUNDED_SCORE_SPIKE"
    assert anomaly["severity"] == "HIGH"

@pytest.mark.asyncio
async def test_section_98_career_value_funnel_calculations(db_session: AsyncSession):
    """
    Validates Section 98:
      Calculates conversion across all 6 stages of the Career Value Funnel.
    """
    funnel = await calculate_career_value_funnel(db_session)
    assert "total_signups" in funnel
    assert len(funnel["funnel_stages"]) == 6
    assert funnel["north_star_metric"]["metric_name"] == "VERIFIED_CAREER_PROGRESS_RATE"

@pytest.mark.asyncio
async def test_section_100_grounded_executive_insights(db_session: AsyncSession):
    """
    Validates Section 100:
      Executive summaries are strictly grounded in empirical database aggregates.
    """
    insights = await generate_grounded_executive_insights(db_session)
    assert insights["verification_seal"] == "EVIDENCE_GROUNDED_ZERO_FABRICATION"
    assert len(insights["insights"]) >= 3
    for ins in insights["insights"]:
        assert ins["confidence"] == "HIGH"
        assert "grounding_metric" in ins
