from fastapi.testclient import TestClient

from core.feature_flags import FeatureFlagManager, LaunchTier
from main import app


def test_feature_flag_tier_defaults_and_evaluation():
    manager = FeatureFlagManager()

    # Tier 1 flag is enabled by default
    assert manager.is_enabled("ats_resume_studio") is True
    assert manager.is_enabled("interview_studio") is True

    # Tier 3 review-gated flag is disabled by default
    assert manager.is_enabled("recruiter_war_room") is False
    assert manager.is_enabled("parent_dashboard") is False

    # Unknown flag fails closed
    assert manager.is_enabled("nonexistent_experimental_feature") is False


def test_feature_flag_kill_switch_and_audit():
    manager = FeatureFlagManager()

    assert manager.is_enabled("jd_matcher") is True
    success = manager.set_kill_switch("jd_matcher", killed=True, actor="security-ops@vireoniq.com")
    assert success is True

    # After kill switch, feature is immediately disabled
    assert manager.is_enabled("jd_matcher") is False

    # Audit log records the event
    logs = manager.get_audit_log()
    assert len(logs) >= 1
    last_log = logs[-1]
    assert last_log["flag_key"] == "jd_matcher"
    assert last_log["action"] == "KILL_SWITCH_ENGAGED"
    assert last_log["actor"] == "security-ops@vireoniq.com"

    # Re-enabling kill switch restores state
    manager.set_kill_switch("jd_matcher", killed=False, actor="security-ops@vireoniq.com")
    assert manager.is_enabled("jd_matcher") is True


def test_feature_flag_user_and_region_restrictions():
    manager = FeatureFlagManager()
    manager._flags["test_custom_flag"] = manager._flags["ats_resume_studio"].__class__(
        key="test_custom_flag",
        description="Region and user test",
        tier=LaunchTier.TIER_2_INVITE_ONLY,
        enabled=True,
        allowed_regions=["US", "IN"],
        allowed_user_ids=["vip_user_123"],
    )

    # Allowed region
    assert manager.is_enabled("test_custom_flag", region="IN") is True
    assert manager.is_enabled("test_custom_flag", region="US") is True
    # Disallowed region
    assert manager.is_enabled("test_custom_flag", region="EU") is False
    # Explicit user bypasses region restriction
    assert manager.is_enabled("test_custom_flag", user_id="vip_user_123", region="EU") is True


def test_system_features_api_endpoint():
    client = TestClient(app)
    res = client.get("/api/v1/system/features")
    assert res.status_code == 200
    data = res.json()
    assert "flags" in data
    assert data["flags"]["ats_resume_studio"] is True
    assert data["flags"]["recruiter_war_room"] is False
