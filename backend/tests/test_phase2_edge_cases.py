import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from services.career_digital_twin_service import generate_career_digital_twin_snapshot
from services.role_comparison_service import compute_candidate_role_alignment
from services.evidence_graph_service import detect_evidence_conflicts

@pytest.mark.asyncio
async def test_candidate_with_zero_evidence(db_session: AsyncSession, test_user):
    """
    Edge case: Candidate with zero evidence must not crash and must not report false weaknesses.
    Every required skill should be reported as UNKNOWN (Insufficient Evidence).
    """
    alignment = await compute_candidate_role_alignment(test_user.id, "Backend Engineer", db_session)
    
    assert alignment["summary"]["matched_count"] == 0
    assert alignment["summary"]["unknown_count"] > 0
    
    for u in alignment["unknown_competencies"]:
        assert u["status"] == "UNKNOWN"
        assert "insufficient evidence" in u["reasoning"].lower()

    snapshot = await generate_career_digital_twin_snapshot(test_user.id, "Backend Engineer", db_session)
    assert snapshot["skills_inventory"]["total_skills"] == 0
    assert snapshot["evidence_summary"]["total_granular_items"] == 0

@pytest.mark.asyncio
async def test_conflict_detection_zero_evidence(db_session: AsyncSession, test_user):
    """
    Edge case: Conflict detector on unknown skill should gracefully report no conflict.
    """
    report = await detect_evidence_conflicts(test_user.id, "NonExistentSkill", db_session)
    assert report["has_conflict"] is False
    assert report["conflict_type"] == "NONE"
