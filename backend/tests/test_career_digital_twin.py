import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from services.career_digital_twin_service import (
    generate_career_digital_twin_snapshot, compute_twin_diff
)
from services.skill_intelligence_service import record_assessment_skill_evidence

@pytest.mark.asyncio
async def test_career_digital_twin_snapshot_synthesis(db_session: AsyncSession, test_user):
    # Add assessed skill
    await record_assessment_skill_evidence(
        user_id=test_user.id,
        skill_name="Python",
        assessment_title="Async IO Mastery",
        score=92.0,
        runtime_complexity="O(N)",
        integrity_score=98.0,
        db=db_session
    )

    snapshot = await generate_career_digital_twin_snapshot(test_user.id, "Backend Engineer", db_session)

    assert "candidate" in snapshot
    assert "career_goals" in snapshot
    assert "career_readiness" in snapshot
    assert "role_alignment" in snapshot
    assert "skills_inventory" in snapshot
    assert "evidence_summary" in snapshot
    assert "snapshot_metadata" in snapshot

    meta = snapshot["snapshot_metadata"]
    assert meta["twin_version"] == "v2.0.0"
    assert "generated_at" in meta
    assert meta["source_versions"]["skills_count"] >= 1

def test_career_twin_diff_engine():
    prev_snapshot = {
        "career_readiness": {"overall_score": 74.0},
        "snapshot_metadata": {
            "generated_at": "2026-08-20T10:00:00Z",
            "source_versions": {"evidence_count": 10, "assessments_count": 1, "projects_count": 2}
        }
    }
    curr_snapshot = {
        "career_readiness": {"overall_score": 78.5},
        "snapshot_metadata": {
            "generated_at": "2026-08-22T10:00:00Z",
            "source_versions": {"evidence_count": 13, "assessments_count": 3, "projects_count": 3}
        }
    }

    diff = compute_twin_diff(prev_snapshot, curr_snapshot)
    assert diff["readiness_delta"] == 4.5
    assert diff["input_deltas"]["assessments_delta"] == 2
    assert diff["input_deltas"]["projects_delta"] == 1
    assert len(diff["explanations"]) >= 2
