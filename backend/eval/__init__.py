"""
VIREONIQ Model Evaluation Framework.

Provides:
- Disjoint entity-level and temporal splitting (`eval.splits`)
- Ranking, calibration, agreement, and selective prediction metrics (`eval.metrics`)
- Perturbation and formatting robustness suites (`eval.robustness`)
- Automated evaluation runner and report generator (`eval.harness`)
"""

from eval.splits import (
    DataLeakageError,
    check_data_leakage,
    create_entity_split,
    create_temporal_split,
)
from eval.metrics import (
    recall_at_k,
    precision_at_k,
    mrr_at_k,
    ndcg_at_k,
    expected_calibration_error,
    cohens_kappa,
    bootstrap_metric_ci,
)
from eval.robustness import RobustnessSuite

__all__ = [
    "DataLeakageError",
    "check_data_leakage",
    "create_entity_split",
    "create_temporal_split",
    "recall_at_k",
    "precision_at_k",
    "mrr_at_k",
    "ndcg_at_k",
    "expected_calibration_error",
    "cohens_kappa",
    "bootstrap_metric_ci",
    "RobustnessSuite",
]
