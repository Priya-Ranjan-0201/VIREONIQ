"""
Evaluation Runner & Machine-Readable Artifact Generator.

Executes evaluation suites and writes results to docs/evals/<run_id>.json.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from eval.metrics import (
    bootstrap_metric_ci,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)


class EvaluationHarness:
    """
    Orchestrates candidate scoring evaluations and serializes audit records.
    """

    def __init__(self, output_dir: Path = Path("docs/evals")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_retrieval_benchmark(
        self,
        test_queries: List[Dict[str, Any]],
        run_name: str = "baseline_retrieval",
    ) -> Dict[str, Any]:
        """
        Runs retrieval evaluation across test queries and persists report JSON.
        """
        recalls_at_5: List[float] = []
        recalls_at_10: List[float] = []
        precisions_at_5: List[float] = []
        ndcgs_at_10: List[float] = []

        for q in test_queries:
            relevant = q.get("relevant_ids", [])
            predicted = q.get("predicted_ids", [])
            graded = q.get("graded_scores", [1.0 if x in relevant else 0.0 for x in predicted])

            recalls_at_5.append(recall_at_k(relevant, predicted, k=5))
            recalls_at_10.append(recall_at_k(relevant, predicted, k=10))
            precisions_at_5.append(precision_at_k(relevant, predicted, k=5))
            ndcgs_at_10.append(ndcg_at_k(graded, k=10))

        mean_r5, ci_r5_low, ci_r5_high = bootstrap_metric_ci(recalls_at_5, lambda s: sum(s) / len(s))
        mean_r10, _, _ = bootstrap_metric_ci(recalls_at_10, lambda s: sum(s) / len(s))
        mean_p5, _, _ = bootstrap_metric_ci(precisions_at_5, lambda s: sum(s) / len(s))
        mean_ndcg10, _, _ = bootstrap_metric_ci(ndcgs_at_10, lambda s: sum(s) / len(s))

        report = {
            "run_name": run_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sample_size": len(test_queries),
            "metrics": {
                "recall_at_5": {"mean": mean_r5, "ci_95": [ci_r5_low, ci_r5_high]},
                "recall_at_10": {"mean": mean_r10},
                "precision_at_5": {"mean": mean_p5},
                "ndcg_at_10": {"mean": mean_ndcg10},
            },
        }

        # Persist machine-readable report
        out_file = self.output_dir / f"{run_name}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report
