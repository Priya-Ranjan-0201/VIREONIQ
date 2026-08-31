import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from services.intervention_service import generate_prescriptive_intervention, get_active_interventions

@pytest.mark.asyncio
async def test_prescriptive_intervention_generation(db_session: AsyncSession, test_user):
    plan_14 = await generate_prescriptive_intervention(test_user.id, "System Design", 14, db_session)
    assert plan_14["gap_skill"] == "System Design"
    assert plan_14["duration_days"] == 14
    assert len(plan_14["milestones"]) == 6
    
    milestone_days = [m["day_range"] for m in plan_14["milestones"]]
    assert "Days 1–3" in milestone_days
    assert "Days 4–7" in milestone_days
    assert "Day 14" in milestone_days

    active = await get_active_interventions(test_user.id, db_session)
    assert len(active) >= 1
    assert active[0]["gap_skill"] == "System Design"
