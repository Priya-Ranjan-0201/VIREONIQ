import pytest

from core.pii_redactor import PIIRedactor
from eval.splits import (
    DataLeakageError,
    check_data_leakage,
    create_entity_split,
    create_temporal_split,
)
from eval.metrics import (
    bootstrap_metric_ci,
    brier_score,
    cohens_kappa,
    expected_calibration_error,
    mrr_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    risk_coverage_curve,
)
from eval.robustness import RobustnessSuite
from eval.harness import EvaluationHarness


def test_entity_split_and_leakage_detector():
    records = [
        {"candidate_id": "c1", "score": 85},
        {"candidate_id": "c1", "score": 90},
        {"candidate_id": "c2", "score": 75},
        {"candidate_id": "c3", "score": 88},
        {"candidate_id": "c4", "score": 92},
        {"candidate_id": "c5", "score": 60},
    ]

    train, val, test = create_entity_split(records, entity_key="candidate_id", train_ratio=0.6, val_ratio=0.2)

    train_cands = {r["candidate_id"] for r in train}
    test_cands = {r["candidate_id"] for r in test}

    # Zero overlap between train and test
    assert len(train_cands.intersection(test_cands)) == 0

    # Explicit leakage detector raises DataLeakageError on overlap
    leaky_test = [{"candidate_id": "c1", "score": 99}]
    with pytest.raises(DataLeakageError, match="Data leakage detected"):
        check_data_leakage(train, leaky_test, entity_key="candidate_id")


def test_temporal_split():
    records = [
        {"id": 1, "created_at": "2026-01-01T00:00:00Z"},
        {"id": 2, "created_at": "2026-03-01T00:00:00Z"},
        {"id": 3, "created_at": "2026-02-01T00:00:00Z"},
    ]
    train, test = create_temporal_split(records, timestamp_key="created_at", split_ratio=0.66)
    assert len(train) == 2
    assert len(test) == 1
    assert train[0]["id"] == 1
    assert train[1]["id"] == 3
    assert test[0]["id"] == 2


def test_evaluation_metrics():
    # 1. Retrieval
    relevant = ["cand_A", "cand_B"]
    predicted = ["cand_A", "cand_C", "cand_B", "cand_D"]

    assert recall_at_k(relevant, predicted, k=1) == 0.5
    assert recall_at_k(relevant, predicted, k=3) == 1.0
    assert precision_at_k(relevant, predicted, k=2) == 0.5
    assert mrr_at_k(relevant, predicted, k=4) == 1.0

    # NDCG
    graded = [3.0, 2.0, 0.0, 1.0]
    assert ndcg_at_k(graded, k=4) > 0.8

    # 2. Calibration
    probs = [0.9, 0.8, 0.2, 0.1]
    outcomes = [1, 1, 0, 0]
    ece = expected_calibration_error(probs, outcomes, num_bins=5)
    assert 0.0 <= ece <= 0.2
    assert brier_score(probs, outcomes) < 0.05

    # 3. Agreement
    rater1 = ["YES", "NO", "YES", "YES"]
    rater2 = ["YES", "NO", "YES", "NO"]
    kappa = cohens_kappa(rater1, rater2)
    assert kappa > 0.4

    # 4. Selective prediction
    curve = risk_coverage_curve(probs, outcomes, num_thresholds=4)
    assert len(curve) > 0
    assert "risk" in curve[0] and "coverage" in curve[0]

    # 5. Bootstrap CI
    data = [0.8, 0.85, 0.9, 0.82, 0.88]
    mean_val, low, high = bootstrap_metric_ci(data, lambda x: sum(x) / len(x), num_bootstraps=100)
    assert low <= mean_val <= high


def test_pii_redaction_and_evaluation():
    redactor = PIIRedactor()
    raw = (
        "Candidate John Doe at john.doe@example.com, mobile +91 9876543210, "
        "Aadhaar 1234-5678-9012, server at 192.168.1.10."
    )
    redacted = redactor.redact(raw)

    assert "john.doe@example.com" not in redacted
    assert "[EMAIL_REDACTED]" in redacted
    assert "9876543210" not in redacted
    assert "[PHONE_REDACTED]" in redacted
    assert "1234-5678-9012" not in redacted
    assert "[GOV_ID_REDACTED]" in redacted
    assert "192.168.1.10" not in redacted
    assert "[IP_REDACTED]" in redacted

    eval_result = redactor.evaluate_redaction([
        (raw, ["john.doe@example.com", "9876543210", "1234-5678-9012"])
    ])
    assert eval_result["recall"] == 1.0


def test_robustness_formatting_and_stuffing():
    # Simulated scoring function
    def score_fn(text: str) -> float:
        base = 0.70
        if "Python" in text:
            base += 0.10
        return round(base, 4)

    # 1. Formatting invariance
    res_inv = RobustnessSuite.test_formatting_invariance(score_fn, "Senior Python Developer with 5 years experience")
    assert res_inv["passed"] is True
    assert res_inv["max_delta"] == 0.0

    # 2. Keyword stuffing resilience
    res_stuff = RobustnessSuite.test_keyword_stuffing_resilience(
        score_fn,
        "Experienced engineer",
        keywords=["Python", "FastAPI"],
        max_acceptable_inflation=0.20,
    )
    assert res_stuff["resilient"] is True


def test_evaluation_harness_output(tmp_path):
    harness = EvaluationHarness(output_dir=tmp_path)
    test_queries = [
        {"relevant_ids": ["c1", "c2"], "predicted_ids": ["c1", "c3", "c2"]},
        {"relevant_ids": ["c4"], "predicted_ids": ["c4", "c5"]},
    ]
    report = harness.run_retrieval_benchmark(test_queries, run_name="test_run")
    assert report["run_name"] == "test_run"
    assert "recall_at_5" in report["metrics"]
    assert (tmp_path / "test_run.json").is_file()
