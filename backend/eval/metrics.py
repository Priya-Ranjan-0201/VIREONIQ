"""
Information Retrieval, Calibration, and Agreement Metrics.

Implements:
1. Retrieval: Recall@k, Precision@k, MRR@k, NDCG@k.
2. Calibration: Expected Calibration Error (ECE), Brier Score.
3. Agreement: Cohen's Kappa for inter-annotator evaluation.
4. Selective Prediction: Risk-coverage curve computation.
5. Statistical Confidence: Bootstrap confidence intervals.
"""

import math
import random
from typing import Any, Callable, Dict, List, Sequence, Tuple


# --- 1. Retrieval & Ranking Metrics ---

def recall_at_k(relevant_items: Sequence[Any], ranked_predictions: Sequence[Any], k: int) -> float:
    """
    Computes Recall@k: fraction of relevant items retrieved in top k.
    """
    if not relevant_items or k <= 0:
        return 0.0
    relevant_set = set(relevant_items)
    top_k = ranked_predictions[:k]
    hits = sum(1 for item in top_k if item in relevant_set)
    return round(hits / len(relevant_set), 4)


def precision_at_k(relevant_items: Sequence[Any], ranked_predictions: Sequence[Any], k: int) -> float:
    """
    Computes Precision@k: fraction of top k predictions that are relevant.
    """
    if not ranked_predictions or k <= 0:
        return 0.0
    top_k = ranked_predictions[:k]
    relevant_set = set(relevant_items)
    hits = sum(1 for item in top_k if item in relevant_set)
    return round(hits / len(top_k), 4)


def mrr_at_k(relevant_items: Sequence[Any], ranked_predictions: Sequence[Any], k: int) -> float:
    """
    Computes Mean Reciprocal Rank (MRR@k).
    """
    relevant_set = set(relevant_items)
    for rank, item in enumerate(ranked_predictions[:k], start=1):
        if item in relevant_set:
            return round(1.0 / rank, 4)
    return 0.0


def ndcg_at_k(relevance_scores: Sequence[float], k: int) -> float:
    """
    Computes Normalized Discounted Cumulative Gain (NDCG@k) from graded relevance scores.
    """
    if not relevance_scores or k <= 0:
        return 0.0

    scores = list(relevance_scores[:k])
    dcg = sum(rel / math.log2(idx + 2) for idx, rel in enumerate(scores))

    ideal_scores = sorted(relevance_scores, reverse=True)[:k]
    idcg = sum(rel / math.log2(idx + 2) for idx, rel in enumerate(ideal_scores))

    if idcg <= 0.0:
        return 0.0
    return round(dcg / idcg, 4)


# --- 2. Calibration & Uncertainty Metrics ---

def expected_calibration_error(
    probabilities: Sequence[float],
    binary_outcomes: Sequence[int],
    num_bins: int = 10,
) -> float:
    """
    Computes Expected Calibration Error (ECE) partitioned across equal probability bins.
    """
    if len(probabilities) != len(binary_outcomes) or not probabilities:
        return 0.0

    n = len(probabilities)
    bin_size = 1.0 / num_bins
    ece = 0.0

    for i in range(num_bins):
        bin_lower = i * bin_size
        bin_upper = (i + 1) * bin_size
        # Gather samples in bin
        indices = [
            idx for idx, p in enumerate(probabilities)
            if (bin_lower <= p < bin_upper) or (i == num_bins - 1 and bin_lower <= p <= bin_upper)
        ]
        if not indices:
            continue

        bin_conf = sum(probabilities[idx] for idx in indices) / len(indices)
        bin_acc = sum(binary_outcomes[idx] for idx in indices) / len(indices)
        ece += (len(indices) / n) * abs(bin_acc - bin_conf)

    return round(ece, 4)


def brier_score(probabilities: Sequence[float], binary_outcomes: Sequence[int]) -> float:
    """
    Computes Brier score: mean squared difference between predicted probabilities and outcomes.
    """
    if len(probabilities) != len(binary_outcomes) or not probabilities:
        return 0.0
    mse = sum((p - y) ** 2 for p, y in zip(probabilities, binary_outcomes)) / len(probabilities)
    return round(mse, 4)


# --- 3. Inter-Annotator Agreement ---

def cohens_kappa(rater_a: Sequence[Any], rater_b: Sequence[Any]) -> float:
    """
    Computes Cohen's Kappa for inter-annotator agreement on discrete ratings.
    """
    if len(rater_a) != len(rater_b) or not rater_a:
        return 0.0

    n = len(rater_a)
    categories = sorted(list(set(rater_a).union(set(rater_b))))
    observed_agreement = sum(1 for a, b in zip(rater_a, rater_b) if a == b) / n

    # Chance agreement
    expected_agreement = 0.0
    for cat in categories:
        p_a = sum(1 for a in rater_a if a == cat) / n
        p_b = sum(1 for b in rater_b if b == cat) / n
        expected_agreement += p_a * p_b

    if expected_agreement >= 1.0:
        return 1.0
    kappa = (observed_agreement - expected_agreement) / (1.0 - expected_agreement)
    return round(kappa, 4)


# --- 4. Selective Prediction & Confidence Intervals ---

def risk_coverage_curve(
    confidences: Sequence[float],
    correctness: Sequence[int],
    num_thresholds: int = 10,
) -> List[Dict[str, float]]:
    """
    Computes coverage and selective risk as abstention threshold increases.
    """
    paired = sorted(zip(confidences, correctness), key=lambda x: x[0], reverse=True)
    curve = []
    total = len(paired)

    for step in range(1, num_thresholds + 1):
        coverage_k = int((step / num_thresholds) * total)
        subset = paired[:coverage_k]
        if not subset:
            continue
        coverage = round(len(subset) / total, 3)
        risk = round(1.0 - (sum(c for _, c in subset) / len(subset)), 4)
        curve.append({"coverage": coverage, "risk": risk})

    return curve


def bootstrap_metric_ci(
    data: Sequence[Any],
    metric_fn: Callable[[Sequence[Any]], float],
    num_bootstraps: int = 500,
    confidence_level: float = 0.95,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """
    Computes (mean, lower_bound, upper_bound) bootstrap confidence intervals.
    """
    if not data:
        return 0.0, 0.0, 0.0

    rng = random.Random(seed)
    n = len(data)
    boot_estimates: List[float] = []

    for _ in range(num_bootstraps):
        resample = [data[rng.randint(0, n - 1)] for _ in range(n)]
        boot_estimates.append(metric_fn(resample))

    boot_estimates.sort()
    alpha = (1.0 - confidence_level) / 2.0
    lower_idx = int(alpha * num_bootstraps)
    upper_idx = int((1.0 - alpha) * num_bootstraps)

    mean_val = sum(boot_estimates) / num_bootstraps
    lower_val = boot_estimates[max(0, lower_idx)]
    upper_val = boot_estimates[min(num_bootstraps - 1, upper_idx)]

    return round(mean_val, 4), round(lower_val, 4), round(upper_val, 4)
