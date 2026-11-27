# Model Card: Hybrid Retrieval & Reciprocal Rank Fusion (RRF)

## Model Details
- **Component**: `BM25Retriever` + Dense Cosine + `reciprocal_rank_fusion` (`backend/services/hybrid_retrieval_portfolio.py`)
- **Version / Status**: `v1.0` — **Shipped**
- **Evaluation Unit**: Candidate/document ranking list `(query, corpus -> top_k)`.

## Intended Use & Out-of-Scope Use
- **Intended Use**: Multi-stage retrieval across skills, job descriptions, and career guidance chunks with human-in-the-loop review.
- **Out-of-Scope Use**: Sole automated selection without human oversight (EU AI Act Annex III high-risk context).

## Metrics vs Baseline & Fairness Findings
- Evaluated on synthetic entity-disjoint benchmarks (`docs/evals/baseline_eval.json`) with Recall@5, Precision@5, NDCG@10, and bootstrap confidence intervals.
- Audited for gender-swap rank overlap stability as a robustness check (explicitly not treated as complete fairness proof).

## Serving & Limitations
- Safe pure-Python/embedding execution (no untrusted pickle artifacts); falls back cleanly to Okapi BM25 if vector service (`Qdrant`) is unavailable.
- Real production recall depends on calibrated target pools and domain-labeled pairs (tracked in `docs/DATA_SOURCES.md`).
