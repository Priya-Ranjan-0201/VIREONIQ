import pytest
import uuid
from services.role_mission_catalog import (
    ROLE_MISSION_CATALOG,
    normalize_target_role,
    TOP_25_MNCS
)
from services.daily_career_os_service import get_todays_career_mission

def test_normalize_target_role():
    assert normalize_target_role("Data Engineer") == "Data Engineer"
    assert normalize_target_role("data engineering") == "Data Engineer"
    assert normalize_target_role("DevOps / SRE") == "DevOps / SRE"
    assert normalize_target_role("Site Reliability Engineer") == "DevOps / SRE"
    assert normalize_target_role("Cloud Architect") == "Cloud Architect"
    assert normalize_target_role("Mobile Engineer") == "Mobile Engineer"
    assert normalize_target_role("iOS Developer") == "Mobile Engineer"
    assert normalize_target_role("Cybersecurity Engineer") == "Cybersecurity Engineer"
    assert normalize_target_role("AI/ML Engineer") == "AI/ML Engineer"
    assert normalize_target_role("Full Stack Engineer") == "Full Stack Engineer"
    assert normalize_target_role("Backend Engineer") == "Backend Engineer"
    assert normalize_target_role(None) == "Backend Engineer"

@pytest.mark.asyncio
async def test_all_eight_roles_in_mission_catalog():
    roles = [
        "AI/ML Engineer",
        "Backend Engineer",
        "Full Stack Engineer",
        "Data Engineer",
        "DevOps / SRE",
        "Cloud Architect",
        "Mobile Engineer",
        "Cybersecurity Engineer"
    ]
    for role in roles:
        assert role in ROLE_MISSION_CATALOG, f"Missing {role} in catalog"
        catalog_entry = ROLE_MISSION_CATALOG[role]
        assert "tasks" in catalog_entry
        assert len(catalog_entry["tasks"]) == 3
        assert "tasks_alt" in catalog_entry
        assert len(catalog_entry["tasks_alt"]) == 3
        assert "active_plan_title" in catalog_entry
        assert "rationale" in catalog_entry

        # Test mission generation for role
        res = await get_todays_career_mission(uuid.uuid4(), target_role=role)
        assert res["target_role"] == role
        assert role.lower() in res["active_plan_title"].lower() or role in res["active_plan_title"]
        assert len(res["tasks"]) == 3
        assert res["is_refreshed"] is False

@pytest.mark.asyncio
async def test_mission_refresh_and_cycle_rotation():
    user_id = uuid.uuid4()
    # Cycle 0 (Set A)
    m0 = await get_todays_career_mission(user_id, "Data Engineer", cycle=0)
    # Cycle 1 (Set B - Alternate)
    m1 = await get_todays_career_mission(user_id, "Data Engineer", cycle=1)
    # Direct refresh flag
    m_ref = await get_todays_career_mission(user_id, "Data Engineer", refresh=True)

    assert m0["is_refreshed"] is False
    assert m1["is_refreshed"] is True
    assert m_ref["is_refreshed"] is True

    # Tasks should be completely different between Cycle 0 and Cycle 1
    t0_titles = [t["title"] for t in m0["tasks"]]
    t1_titles = [t["title"] for t in m1["tasks"]]
    assert t0_titles != t1_titles
    assert "DENSE_RANK" in t0_titles[0]
    assert "Trapping Rain Water" in t1_titles[0]
