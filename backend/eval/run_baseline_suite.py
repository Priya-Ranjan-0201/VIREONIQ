"""
Deterministic Baseline Evaluation & Artifact Generator (Phases 6, 8, 9, 12, 13).

Executes the offline fixture benchmarks using EvaluationHarness, ModelGateAuditor,
HybridRetrievalPortfolio, ResponsibleAIEngine, and RedTeamSuite, writing JSON and
Markdown summary artifacts to `docs/evals/`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from eval.harness import EvaluationHarness  # noqa: E402
from eval.model_gate import ModelGateAuditor  # noqa: E402
from eval.redteam import RedTeamSuite  # noqa: E402
from services.hybrid_retrieval_portfolio import BM25Retriever, reciprocal_rank_fusion  # noqa: E402
from services.responsible_ai import ResponsibleAIEngine  # noqa: E402


def main() -> None:
    eval_dir = REPO_ROOT / "docs" / "evals"
    harness = EvaluationHarness(output_dir=eval_dir)

    corpus = [
        {"id": "doc_py_api", "text": "FastAPI async PostgreSQL Redis distributed backend microservices"},
        {"id": "doc_ml_rag", "text": "PyTorch RAG Qdrant hybrid retrieval cross encoder reranking"},
        {"id": "doc_fe_ts", "text": "React TypeScript strict Vite Tailwind Vitest UI design"},
        {"id": "doc_sec_ops", "text": "Docker Kubernetes Trivy SBOM security telemetry Prometheus"},
        {"id": "doc_unrelated", "text": "Culinary pastry baking sourdough fermentation oven recipes"},
    ]
    bm25 = BM25Retriever(corpus)

    # Fixture queries comparing BM25 baseline vs RRF hybrid fusion
    fixture_queries: List[Dict[str, Any]] = [
        {
            "relevant_ids": ["doc_py_api"],
            "bm25": bm25.search("FastAPI PostgreSQL Redis", top_k=5),
            "dense": [("doc_py_api", 0.91), ("doc_sec_ops", 0.62), ("doc_ml_rag", 0.41)],
        },
        {
            "relevant_ids": ["doc_ml_rag"],
            "bm25": bm25.search("RAG Qdrant retrieval", top_k=5),
            "dense": [("doc_ml_rag", 0.94), ("doc_py_api", 0.55), ("doc_fe_ts", 0.25)],
        },
        {
            "relevant_ids": ["doc_fe_ts"],
            "bm25": bm25.search("React TypeScript Vite", top_k=5),
            "dense": [("doc_fe_ts", 0.89), ("doc_py_api", 0.30), ("doc_ml_rag", 0.20)],
        },
    ]

    bm25_eval_inputs = [
        {"relevant_ids": q["relevant_ids"], "predicted_ids": [d for d, _ in q["bm25"]]}
        for q in fixture_queries
    ]
    rrf_eval_inputs = [
        {
            "relevant_ids": q["relevant_ids"],
            "predicted_ids": [d for d, _ in reciprocal_rank_fusion([q["bm25"], q["dense"]], top_k=5)],
        }
        for q in fixture_queries
    ]

    bm25_report = harness.run_retrieval_benchmark(bm25_eval_inputs, run_name="bm25_baseline")
    rrf_report = harness.run_retrieval_benchmark(rrf_eval_inputs, run_name="hybrid_rrf_baseline")

    dual_audit = ResponsibleAIEngine.audit_competence_and_fairness(
        qualified_scores=[84.0, 88.0, 91.0, 86.0],
        unqualified_control_scores=[34.0, 41.0, 38.0, 45.0],
        group_a_scores=[84.0, 88.0, 41.0, 45.0],
        group_b_scores=[86.0, 91.0, 34.0, 38.0],
    )
    redteam_report = RedTeamSuite.run_all()

    gate_result = ModelGateAuditor.audit_model(
        "hybrid_retrieval_rrf",
        {
            "model_score": rrf_report["metrics"]["ndcg_at_10"]["mean"],
            "baseline_score": 0.65,
            "entity_overlap_count": 0,
            "temporal_leakage": False,
            "repeatability_variance": 0.0,
            "demographic_disparity": 0.0,
            "max_formatting_delta": 0.01,
            "ece": 0.05,
            "p95_latency_ms": 12.0,
            "latency_budget_ms": 200.0,
        },
    )

    combined = {
        "suite": "deterministic_fixture_eval_v1",
        "bm25_baseline": bm25_report,
        "hybrid_rrf": rrf_report,
        "responsible_ai_dual_audit": dual_audit,
        "redteam": redteam_report,
        "model_gate": gate_result.to_dict(),
    }

    (eval_dir / "baseline_eval.json").write_text(json.dumps(combined, indent=2), encoding="utf-8")

    md = "\n".join([
        "# VIREONIQ Deterministic Fixture Evaluation Report",
        "",
        "> Executed offline using deterministic synthetic fixtures (`backend/eval/run_baseline_suite.py`).",
        "> Results reflect synthetic fixture verification only, not live hiring outcome validity.",
        "",
        "## 1. Retrieval Benchmark (Fixture N=3)",
        f"- **BM25 Recall@5**: `{bm25_report['metrics']['recall_at_5']['mean']:.4f}`",
        f"- **Hybrid RRF Recall@5**: `{rrf_report['metrics']['recall_at_5']['mean']:.4f}`",
        f"- **Hybrid RRF NDCG@10**: `{rrf_report['metrics']['ndcg_at_10']['mean']:.4f}`",
        "",
        "## 2. Responsible AI Dual Validation (Synthetic Paired Fixture)",
        f"- **Discernment Delta (Qualified vs Unqualified)**: `{dual_audit['discernment_delta']}`",
        f"- **Adverse Impact Ratio (AIR)**: `{dual_audit['adverse_impact_ratio']}`",
        f"- **Illusion of Neutrality Flagged**: `{dual_audit['illusion_of_neutrality_flagged']}`",
        "",
        "## 3. OWASP LLM 2025 Red-Team Suite",
        f"- **Probes Passed**: `{redteam_report['passed_probes']} / {redteam_report['total_probes']}`",
        "",
        "## 4. Model Gate Audit (`hybrid_retrieval_rrf`)",
        f"- **Overall Passed**: `{gate_result.overall_passed}`",
    ])
    (eval_dir / "baseline_eval.md").write_text(md + "\n", encoding="utf-8")
    print(f"Wrote baseline evaluation artifacts to {eval_dir}")


if __name__ == "__main__":
    main()
