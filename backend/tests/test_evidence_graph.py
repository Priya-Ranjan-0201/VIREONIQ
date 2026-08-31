import pytest
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from services.evidence_graph_service import (
    record_granular_evidence, determine_freshness_state,
    detect_evidence_conflicts, trace_skill_lineage
)

def test_freshness_state_classification():
    now = datetime.now(timezone.utc)
    
    # 2 months old -> FRESH
    state_2m, decay_2m = determine_freshness_state(now - timedelta(days=60))
    assert state_2m == "FRESH"
    assert decay_2m >= 90.0

    # 8 months old -> AGING
    state_8m, decay_8m = determine_freshness_state(now - timedelta(days=240))
    assert state_8m == "AGING"

    # 18 months old -> STALE
    state_18m, decay_18m = determine_freshness_state(now - timedelta(days=540))
    assert state_18m == "STALE"

    # 30 months old -> EXPIRED
    state_30m, decay_30m = determine_freshness_state(now - timedelta(days=900))
    assert state_30m == "EXPIRED"

@pytest.mark.asyncio
async def test_evidence_deduplication_and_lineage(db_session: AsyncSession, test_user):
    # 1. Add project from Resume
    ev1 = await record_granular_evidence(
        user_id=test_user.id,
        skill_name="Python",
        evidence_type="RESUME_CLAIM",
        source="RESUME_PDF",
        source_span="Built high-throughput backend services using Python and FastAPI",
        source_group="project:ecommerce-backend",
        status="CLAIMED",
        db=db_session
    )
    assert ev1["is_duplicate_linked"] is False

    # 2. Add same project from GitHub (should be deduplication-linked)
    ev2 = await record_granular_evidence(
        user_id=test_user.id,
        skill_name="Python",
        evidence_type="PROJECT_REPO",
        source="GITHUB_REPO",
        source_reference="https://github.com/alex/ecommerce-backend",
        source_group="project:ecommerce-backend",
        status="DEMONSTRATED",
        db=db_session
    )
    assert ev2["is_duplicate_linked"] is True

    # 3. Lineage trace
    lineage = await trace_skill_lineage(test_user.id, "Python", db_session)
    assert lineage["total_lineage_nodes"] >= 2
    assert len(lineage["lineage_events"]) >= 2

@pytest.mark.asyncio
async def test_evidence_conflict_detection(db_session: AsyncSession, test_user):
    # Self-claim on resume
    await record_granular_evidence(
        user_id=test_user.id,
        skill_name="System Design",
        evidence_type="RESUME_CLAIM",
        source="RESUME_PDF",
        source_span="Expert in distributed systems design",
        status="CLAIMED",
        db=db_session
    )

    # Low assessment score
    await record_granular_evidence(
        user_id=test_user.id,
        skill_name="System Design",
        evidence_type="CODING_ASSESSMENT",
        source="JUDGE0_SANDBOX",
        status="ASSESSED",
        metadata_payload={"score": 45.0},
        db=db_session
    )

    conflict = await detect_evidence_conflicts(test_user.id, "System Design", db_session)
    assert conflict["has_conflict"] is True
    assert conflict["conflict_type"] == "CLAIM_VS_ASSESSMENT_DISCREPANCY"
    assert "remediation" in conflict["recommended_action"].lower() or "sandbox" in conflict["recommended_action"].lower()
