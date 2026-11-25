import pytest

from services.responsible_ai import (
    AutonomyGuardError,
    ResponsibleAIEngine,
)


def test_dual_validation_passes_competent_and_fair_system():
    # Qualified candidates score high; unqualified score low (clear discernment)
    qual = [85.0, 90.0, 88.0, 92.0]
    unqual = [45.0, 50.0, 48.0, 52.0]

    # Demographic groups have similar selection rates above 70.0
    group_a = [85.0, 90.0, 50.0, 45.0]  # 50% pass rate
    group_b = [88.0, 92.0, 48.0, 52.0]  # 50% pass rate

    res = ResponsibleAIEngine.audit_competence_and_fairness(
        qualified_scores=qual,
        unqualified_control_scores=unqual,
        group_a_scores=group_a,
        group_b_scores=group_b,
        pass_threshold=70.0,
    )

    assert res["overall_audit_passed"] is True
    assert res["competence_discernment_passed"] is True
    assert res["four_fifths_rule_passed"] is True
    assert res["illusion_of_neutrality_flagged"] is False
    assert res["discernment_delta"] >= 35.0


def test_dual_validation_flags_illusion_of_neutrality():
    # Model gives everyone similar mediocre scores regardless of qualification
    qual = [65.0, 66.0, 64.0]
    unqual = [63.0, 65.0, 64.0]  # Discernment near zero (< 15 pts)

    # Demographic parity looks artificially perfect
    group_a = [65.0, 66.0, 64.0]
    group_b = [64.0, 65.0, 66.0]

    res = ResponsibleAIEngine.audit_competence_and_fairness(
        qualified_scores=qual,
        unqualified_control_scores=unqual,
        group_a_scores=group_a,
        group_b_scores=group_b,
        pass_threshold=60.0,
    )

    # Should flag illusion of neutrality!
    assert res["illusion_of_neutrality_flagged"] is True
    assert res["competence_discernment_passed"] is False
    assert res["overall_audit_passed"] is False


def test_autonomy_guard_blocks_unauthorized_high_impact_actions():
    # Unauthorized high-impact action is blocked
    with pytest.raises(AutonomyGuardError, match="high-impact operation"):
        ResponsibleAIEngine.enforce_agency_guard("APPLY_JOB", user_confirmed=False)

    with pytest.raises(AutonomyGuardError, match="high-impact operation"):
        ResponsibleAIEngine.enforce_agency_guard("MESSAGE_RECRUITER", user_confirmed=False)

    # Confirmed high-impact action is allowed
    approved = ResponsibleAIEngine.enforce_agency_guard("APPLY_JOB", user_confirmed=True)
    assert approved["status"] == "APPROVED"
    assert approved["confirmed_by_user"] is True

    # Low-impact actions proceed without special confirmation
    low_impact = ResponsibleAIEngine.enforce_agency_guard("VIEW_RECOMMENDATIONS", user_confirmed=False)
    assert low_impact["status"] == "APPROVED"
    assert low_impact["is_high_impact"] is False


def test_reviewer_telemetry_computes_accurate_rates():
    decisions = [
        {"id": 1, "overridden": False},
        {"id": 2, "overridden": True},
        {"id": 3, "overridden": False},
        {"id": 4, "overridden": False},
    ]

    telemetry = ResponsibleAIEngine.compute_reviewer_telemetry(decisions)
    assert telemetry["total_reviews"] == 4
    assert telemetry["override_count"] == 1
    assert telemetry["override_rate"] == 0.25
    assert telemetry["agreement_rate"] == 0.75
