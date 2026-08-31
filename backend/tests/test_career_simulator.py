import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from services.career_simulator_service import simulate_counterfactual_scenario, generate_career_pathways

@pytest.mark.asyncio
async def test_what_if_counterfactual_simulation(db_session: AsyncSession, test_user):
    result = await simulate_counterfactual_scenario(
        user_id=test_user.id,
        target_role_name="Backend Engineer",
        action_type="IMPROVE_SYSTEM_DESIGN",
        action_parameter="System Design",
        db=db_session
    )
    
    assert "baseline_readiness" in result
    assert "projected_readiness" in result
    assert result["projected_readiness"] >= result["baseline_readiness"]
    assert "confidence_interval" in result
    assert "lower_bound" in result["confidence_interval"]
    assert "upper_bound" in result["confidence_interval"]
    assert result["confidence_interval"]["lower_bound"] <= result["projected_readiness"] <= result["confidence_interval"]["upper_bound"]

@pytest.mark.asyncio
async def test_multi_path_career_trajectories(db_session: AsyncSession, test_user):
    paths = await generate_career_pathways(test_user.id, "Backend Engineer", db_session)
    assert len(paths) == 4
    
    path_ids = [p["path_id"] for p in paths]
    assert "fastest" in path_ids
    assert "lowest_effort" in path_ids
    assert "highest_opportunity" in path_ids
    assert "closest_match" in path_ids

    for p in paths:
        assert "milestones" in p
        assert "tradeoff_analysis" in p
        assert "duration_weeks" in p
