# Model Card: Hybrid Retrieval & RRF Portfolio

- **Component ID**: `hybrid_retrieval_rrf`
- **Status**: Shipped (Deterministic Lexical + Vector Fusion Baseline)
- **Evaluation Unit**: Candidate-query / job-description ranked list

## 1. Intended Use & Scope
- Ranks job postings, learning blueprints, and candidate evidence passages by fusing Okapi BM25 lexical scores with dense cosine similarity via Reciprocal Rank Fusion (`c = 60`).
- Evaluated end-to-end across retrieval stages (`eval/run_baseline_suite.py`).

## 2. Out-of-Scope Use
- Not validated for autonomous finalist selection or employment ranking without human review (classified high-risk if used for employer screening under EU AI Act Annex III / NYC LL144).

## 3. Baseline & Evaluation Metrics
- Beats single-stream BM25 on multi-view synthetic evaluation fixtures (`docs/evals/baseline_eval.json`).
- Evaluated with entity-disjoint splits (`eval/splits.py`) verified leak-free by `test_data_evaluation.py`.

## 4. Failure Modes & Limitations
- Synthetic test fixtures cannot prove real-world labor-market generalization; real licensed benchmark integration (ESCO / TalentCLEF) is pending maintainer dataset sign-off in `docs/DATA_SOURCES.md`.
- Cross-lingual synonym drops require explicit taxonomy mapping or multilingual encoders.
