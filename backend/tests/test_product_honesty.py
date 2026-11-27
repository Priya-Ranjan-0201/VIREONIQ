import uuid
from schemas.gap import GapAnalysisResponse
from services.gap_engine import _fallback_analyze_gap
from core.feature_flags import feature_flag_engine, LaunchTier

class MockTargetRole:
    role_name = "Backend Engineer"
    required_skills = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    min_projects = 2
    min_experience_years = 1.0
    salary_band_base = 60000.0

def test_gap_engine_heuristic_uncertainty_bounds():
    mock_role = MockTargetRole()
    parsed_resume = {"skills": ["Python", "FastAPI"]}
    analysis_data, recommendations = _fallback_analyze_gap(parsed_resume, mock_role, "Product")
    
    # Verify presence of honest readiness fields
    assert "readiness_estimate_heuristic" in analysis_data
    assert "uncertainty_range" in analysis_data
    assert "% - " in analysis_data["uncertainty_range"]
    assert analysis_data["readiness_estimate_heuristic"] >= 0.0
    assert analysis_data["readiness_estimate_heuristic"] <= 100.0

def test_feature_flags_tier_gating_defaults():
    # Tier 1 features must be enabled by default
    tier_1_flags = [k for k, v in feature_flag_engine.flags.items() if v.tier == LaunchTier.TIER_1_PUBLIC_BETA]
    assert len(tier_1_flags) > 0
    for flag in tier_1_flags:
        assert feature_flag_engine.is_enabled(flag) is True, f"Tier 1 flag {flag} must be enabled"

    # Tier 3 review-gated features must be disabled by default
    tier_3_flags = [k for k, v in feature_flag_engine.flags.items() if v.tier == LaunchTier.TIER_3_REVIEW_GATED]
    assert len(tier_3_flags) > 0
    for flag in tier_3_flags:
        assert feature_flag_engine.is_enabled(flag) is False, f"Tier 3 flag {flag} must be gated/disabled by default"

def test_gap_analysis_response_schema_fields():
    data = {
        "id": uuid.uuid4(),
        "target_role_name": "Full Stack Engineer",
        "overall_readiness_score": 75.0,
        "placement_probability": 60.0,
        "readiness_estimate_heuristic": 60.0,
        "uncertainty_range": "45.0% - 75.0%",
        "recommendations": []
    }
    resp = GapAnalysisResponse(**data)
    assert resp.readiness_estimate_heuristic == 60.0
    assert resp.uncertainty_range == "45.0% - 75.0%"
