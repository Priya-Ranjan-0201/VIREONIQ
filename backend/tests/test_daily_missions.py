import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from services.daily_mission_service import get_or_generate_daily_mission, toggle_task_completion

@pytest.mark.asyncio
async def test_daily_mission_lifecycle(db_session: AsyncSession, test_user):
    mission = await get_or_generate_daily_mission(test_user.id, "Backend Engineer", db_session)
    
    assert "tasks" in mission
    assert len(mission["tasks"]) >= 3
    assert mission["total_estimated_minutes"] > 0
    assert mission["total_projected_delta"] > 0
    assert mission["completion_rate"] == 0.0
    assert mission["is_completed"] is False

    # Toggle first task
    first_task_id = mission["tasks"][0]["id"]
    updated = await toggle_task_completion(test_user.id, first_task_id, True, db_session)
    assert updated["completion_rate"] > 0.0

    # Verify task status persisted
    task_map = {t["id"]: t["completed"] for t in updated["tasks"]}
    assert task_map[first_task_id] is True
