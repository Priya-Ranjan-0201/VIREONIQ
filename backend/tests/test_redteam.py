from eval.redteam import RedTeamSuite


def test_redteam_suite_passes_all_deterministic_probes():
    report = RedTeamSuite.run_all()
    assert report["total_probes"] == 5
    assert report["passed_probes"] == 5
    assert report["all_passed"] is True
