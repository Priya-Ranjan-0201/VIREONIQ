# VIREONIQ Deterministic Fixture Evaluation Report

> Executed offline using deterministic synthetic fixtures (`backend/eval/run_baseline_suite.py`).
> Results reflect synthetic fixture verification only, not live hiring outcome validity.

## 1. Retrieval Benchmark (Fixture N=3)
- **BM25 Recall@5**: `1.0000`
- **Hybrid RRF Recall@5**: `1.0000`
- **Hybrid RRF NDCG@10**: `1.0000`

## 2. Responsible AI Dual Validation (Synthetic Paired Fixture)
- **Discernment Delta (Qualified vs Unqualified)**: `47.75`
- **Adverse Impact Ratio (AIR)**: `1.0`
- **Illusion of Neutrality Flagged**: `False`

## 3. OWASP LLM 2025 Red-Team Suite
- **Probes Passed**: `5 / 5`

## 4. Model Gate Audit (`hybrid_retrieval_rrf`)
- **Overall Passed**: `True`
