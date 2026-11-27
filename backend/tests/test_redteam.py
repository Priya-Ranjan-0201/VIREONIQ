from eval.redteam import run_redteam_suite


def test_deterministic_redteam_suite_passes():
    report = run_redteam_suite()
    assert report["total_probes"] == 6
    assert report["all_passed"] is True, f"Failed probes: {[p for p in report['probes'] if not p['passed']]}"
