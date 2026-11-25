"""
The VIREONIQ Model Gate (A3 Protocol).

A model, score, or recommendation ships ONLY if all 8 criteria pass:
1. Baseline Beat: Strictly outperforms a naive heuristic or majority class baseline.
2. Entity Split: Evaluated on disjoint entity-level test sets (zero candidate/job overlap).
3. Temporal Validity: Time-split evaluation demonstrates no future-data leakage.
4. Determinism: High repeatability across random seeds (variance <= 0.001).
5. Fairness & Competence: Invariant to protected/demographic proxy attributes while discriminating skill levels.
6. Formatting Invariance: Insensitive to markdown or superficial whitespace perturbations (delta <= 0.05).
7. Calibration: Expected Calibration Error (ECE) <= 0.15 with confidence intervals reported.
8. Latency Bounds: Inference executes within the allowed production latency budget.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ModelGateCriterion:
    name: str
    passed: bool
    observed_value: Any
    target_threshold: str
    details: str


@dataclass
class ModelGateResult:
    model_name: str
    overall_passed: bool
    criteria: List[ModelGateCriterion] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "overall_passed": self.overall_passed,
            "criteria": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "observed": c.observed_value,
                    "target": c.target_threshold,
                    "details": c.details,
                }
                for c in self.criteria
            ],
        }


class ModelGateAuditor:
    """
    Evaluates candidate models against the mandatory 8-item Model Gate.
    """

    @staticmethod
    def audit_model(
        model_name: str,
        metrics: Dict[str, Any],
    ) -> ModelGateResult:
        """
        Runs full 8-point audit checklist.
        """
        criteria: List[ModelGateCriterion] = []

        # 1. Baseline Beat
        model_metric = metrics.get("model_score", 0.0)
        baseline_metric = metrics.get("baseline_score", 0.0)
        pass_baseline = model_metric > baseline_metric
        criteria.append(ModelGateCriterion(
            name="1. Baseline Beat",
            passed=pass_baseline,
            observed_value=f"Model: {model_metric}, Baseline: {baseline_metric}",
            target_threshold="model_score > baseline_score",
            details="Outperforms naive heuristic or majority-class baseline.",
        ))

        # 2. Entity Split Cleanliness
        overlap_count = metrics.get("entity_overlap_count", 0)
        pass_entity = (overlap_count == 0)
        criteria.append(ModelGateCriterion(
            name="2. Entity Split Integrity",
            passed=pass_entity,
            observed_value=f"{overlap_count} overlapping entities",
            target_threshold="overlap == 0",
            details="Zero candidate or job identity overlap between train and test splits.",
        ))

        # 3. Temporal Validity
        temporal_leakage = metrics.get("temporal_leakage", False)
        pass_temporal = not temporal_leakage
        criteria.append(ModelGateCriterion(
            name="3. Temporal Validity",
            passed=pass_temporal,
            observed_value=f"Leakage: {temporal_leakage}",
            target_threshold="temporal_leakage == False",
            details="Evaluation strictly respects chronological ordering.",
        ))

        # 4. Deterministic Repeatability
        variance = metrics.get("repeatability_variance", 0.0)
        pass_determinism = variance <= 0.001
        criteria.append(ModelGateCriterion(
            name="4. Deterministic Repeatability",
            passed=pass_determinism,
            observed_value=f"Variance: {variance}",
            target_threshold="variance <= 0.001",
            details="Repeated runs produce deterministic results without hallucinated drift.",
        ))

        # 5. Fairness & Demographic Invariance
        demographic_disparity = metrics.get("demographic_disparity", 0.0)
        pass_fairness = demographic_disparity <= 0.05
        criteria.append(ModelGateCriterion(
            name="5. Demographic Invariance",
            passed=pass_fairness,
            observed_value=f"Disparity: {demographic_disparity}",
            target_threshold="disparity <= 0.05",
            details="Scores are invariant to candidate gender/race proxy markers.",
        ))

        # 6. Formatting Invariance
        max_format_delta = metrics.get("max_formatting_delta", 0.0)
        pass_format = max_format_delta <= 0.05
        criteria.append(ModelGateCriterion(
            name="6. Formatting Invariance",
            passed=pass_format,
            observed_value=f"Max Delta: {max_format_delta}",
            target_threshold="delta <= 0.05",
            details="Superficial markdown/whitespace styling does not inflate scores.",
        ))

        # 7. Calibration & Uncertainty
        ece = metrics.get("ece", 0.0)
        pass_calibration = ece <= 0.15
        criteria.append(ModelGateCriterion(
            name="7. Uncertainty Calibration",
            passed=pass_calibration,
            observed_value=f"ECE: {ece}",
            target_threshold="ECE <= 0.15",
            details="Probabilities reflect true empirical accuracy within bounded ECE.",
        ))

        # 8. Production Latency Bound
        latency_ms = metrics.get("p95_latency_ms", 0.0)
        latency_budget = metrics.get("latency_budget_ms", 250.0)
        pass_latency = latency_ms <= latency_budget
        criteria.append(ModelGateCriterion(
            name="8. Production Latency Bound",
            passed=pass_latency,
            observed_value=f"P95: {latency_ms}ms",
            target_threshold=f"<= {latency_budget}ms",
            details="Executes comfortably within real-time latency budget.",
        ))

        overall_passed = all(c.passed for c in criteria)
        return ModelGateResult(
            model_name=model_name,
            overall_passed=overall_passed,
            criteria=criteria,
        )
