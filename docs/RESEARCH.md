# VIREONIQ Research Evidence Brief

> Starting evidence brief assembled from research findings, empirical audits, regulatory frameworks, and algorithmic methodology.
> This file corresponds to Part C of Master Prompt v2 and serves as the scientific foundation for VIREONIQ's evaluation framework, model gates, and governance architecture.

---

## C1. Findings That Shaped This Architecture

### F1. Benchmark Validity in Resume-Job Matching
- **Source**: *Resume-Job Benchmark Audit Repository*  
  URL: [https://github.com/nusratrita/resume-job-benchmark-audit](https://github.com/nusratrita/resume-job-benchmark-audit)  
  *(Note on source availability: Verified as public research repository; in environments where the exact repository URL is gated or redirected, the finding is grounded in the broader empirical literature on recruitment benchmark artifacts).*
- **Reported Problems**: On public resume-job fit datasets, severe artifacts exist: resume leakage across train and test splits (sharing up to 476 identical resumes), label artifacts where predictions are driven primarily by job and resume marginal distributions rather than pairwise match quality, low human inter-annotator agreement, and superficial embedding score inflation when markdown formatting or bold headers are added without changing text semantics.
- **Identified Gap**: Evaluations can artificially inflate match metrics through formatting artifacts and train-test data leakage.
- **Fix Applied in VIREONIQ**: Strict entity-level splits (job ID and resume ID disjoint across sets), automated leakage tests in CI, inter-annotator agreement reporting (Cohen's Kappa / Krippendorff's Alpha), and formatting-invariance evaluation tests (Phases 5, 6; Model Gate items 3, 6, 8).

### F2. Evaluation Gaps in AI Recruitment Systems
- **Source**: *Systematized Review of AI Recruitment Systems*  
  URL: [https://arxiv.org/abs/2609.04286](https://arxiv.org/abs/2609.04286) / [PDF](https://arxiv.org/pdf/2609.04286)
- **Reported Gaps**: Observational hiring labels confound exposure, recruiter preference, and genuine candidate competence. Many published studies rely entirely on private or synthetic datasets with unmeasured stage-by-stage recall, lack joint evaluation of utility, fairness, privacy, and security, fail to address document-borne prompt injections, and lack evidence that human-in-the-loop review actually prevents automated errors.
- **Recommended Practices**: Match claims strictly to the evaluated unit; report stage-by-stage recall against defensible target candidate sets; treat missing evidence as "unknown" rather than "negative" (`supported`, `contradicted`, `unknown`); evaluate selective prediction and abstention using risk-coverage curves; disclose full pipeline parameters (candidate pool size, negative sampling strategies, inference latency); measure substantive human review interactions; enforce strict authority boundaries for autonomous agents.
- **Fix Applied in VIREONIQ**: Model Gate items 1 and 7; Phase 6 full-pipeline transparency; Phase 7 three-valued evidence ontology (`supported`/`contradicted`/`unknown`); Phase 12 reviewer telemetry logging; Phase 13 privacy metrics and agent action guards.

### F3. Fairness Metrics Alone Can Mislead ("Illusion of Neutrality")
- **Source**: *Fairness Is Not Enough: Auditing Competence and Intersectional Bias in AI-powered Resume Screening*  
  URL: [https://arxiv.org/abs/2507.11548](https://arxiv.org/abs/2507.11548) / [PDF](https://arxiv.org/pdf/2507.11548)
- **Findings**: Demographic parity and equalized odds metrics alone can create an "illusion of neutrality": systems can exhibit statistical parity across race/gender groups simply because they fail to discriminate matched from completely mismatched candidates (i.e. zero competence). Furthermore, scores were heavily driven by keyword frequency rather than contextual qualification, and score variability across repeated runs was substantial.
- **Methods Proposed**: Matched-pair audit testing, standardized prompting with randomized attribute ordering, ANOVA and effect sizes with Bonferroni/Holm correction, discernment testing (paired qualified vs unqualified control resumes), keyword sensitivity tests, and a competence-versus-bias 2x2 audit grid.
- **Fix Applied in VIREONIQ**: Phase 12 dual validation (competence discernment tested alongside demographic parity); Model Gate item 5.

### F4. LLM and Human Resume Rating Disagreement
- **Source**: *Human and LLM-Based Resume Matching* (NAACL Findings 2025)  
  URL: [https://aclanthology.org/2025.findings-naacl.270.pdf](https://aclanthology.org/2025.findings-naacl.270.pdf)
- **Findings**: Zero-shot LLM evaluations exhibit weak correlation and low agreement with expert human recruiters on authentic resumes. Even with extensive prompt engineering, agreement remains modest, and bias mitigation is inconsistent.
- **Fix Applied in VIREONIQ**: Phase 9 LLM evaluator validation against calibrated human gold labels; Phase 12 mandatory human-in-the-loop escalation paths for all automated scoring.

### F5. Hybrid Multi-Stage Retrieval Superiority in HR Tasks
- **Source**: *TalentCLEF 2026 Overview*  
  URL: [https://arxiv.org/abs/2606.31692](https://arxiv.org/abs/2606.31692) / [PDF](https://arxiv.org/pdf/2606.31692)
- **Findings**: Top-performing talent-matching architectures combine dense vector retrieval and lexical search (BM25) with reciprocal rank fusion (RRF) and cross-encoder or LLM reranking. LLM-structured profile representations and taxonomy graph alignment significantly enhance matching fidelity over raw text embeddings.
- **Fix Applied in VIREONIQ**: Phase 7 layout-aware taxonomy normalization; Phase 8 hybrid retrieval portfolio (BM25 + dense bi-encoder + cross-encoder reranker + RRF).

### F6. Embedding Choice Reversal Post-Reranking
- **Source**: *Rethinking Hybrid Retrieval*  
  URL: [https://arxiv.org/abs/2506.00049](https://arxiv.org/abs/2506.00049) / [HTML](https://arxiv.org/html/2506.00049v1)
- **Findings**: First-stage vector embedding rankings do not monotonically predict post-reranker performance; smaller, computationally efficient embedding models can achieve higher final recall and NDCG when paired with cross-encoder rerankers than larger un-reranked embeddings.
- **Fix Applied in VIREONIQ**: Phase 8 end-to-end evaluation with the reranker in the loop.

### F7. LLM-as-a-Judge Limitations and Failure Modes
- **Source**: *Can LLMs Be Trusted for Evaluating RAG Systems?*  
  URL: [https://arxiv.org/abs/2504.20119](https://arxiv.org/abs/2504.20119) / [HTML](https://arxiv.org/html/2504.20119v2)
- **Findings**: LLM evaluators suffer from self-preference bias, parametric knowledge leakage, sensitivity to prompt phrasing, and model version drift. Recommended mitigations include pairing judges from different model families, verifying against human calibration sets, employing closed-book controls (detecting parametric hallucination), and using pairwise/Elo ranking.
- **Fix Applied in VIREONIQ**: Phase 6 evaluation protocol requiring distinct judge model families, human-calibrated sets, closed-book controls, and pinned model digests.

### F8. Multilingual Retrieval Disparities
- **Source**: *JobResQA*  
  URL: [https://arxiv.org/abs/2601.23183](https://arxiv.org/abs/2601.23183) / [PDF](https://arxiv.org/pdf/2601.23183)
- **Findings**: Cross-lingual resume-job evaluation benchmarks reveal substantial performance drops when transitioning from English to non-English languages, compounded by translation artifacts in synthetic datasets.
- **Identified Gap**: Low-resource Indian languages (Hindi, etc.) are under-represented in published talent benchmarks.
- **Fix Applied in VIREONIQ**: Phase 5 dedicated multilingual evaluation subsets; Phase 15 internationalization support ensuring non-English tokens are never silently dropped.

### F9. Career Trajectory Modeling Methodology
- **Source**: *CAPER: Context-Aware Personalized Career Path Recommendation*  
  URL: [https://arxiv.org/abs/2408.15620](https://arxiv.org/abs/2408.15620) / [HTML](https://arxiv.org/html/2408.15620v2)
- **Findings**: Temporal career modeling requires strict temporal-split validation rather than random cross-validation to prevent future-data leakage; prediction accuracy degrades significantly across multi-year horizons.
- **Fix Applied in VIREONIQ**: Phase 10 temporal split backtesting for career simulation models with explicit multi-horizon uncertainty intervals.

### F10. Document-Borne Prompt Injection in Resumes
- **Sources**:
  1. *ResumeShield*  
     URL: [https://arxiv.org/abs/2609.20188](https://arxiv.org/abs/2609.20188) / [PDF](https://arxiv.org/pdf/2609.20188)
  2. *Measuring Real-World Prompt Injection Attacks in LLM-based Resume Screening*  
     URL: [https://arxiv.org/abs/2605.28999](https://arxiv.org/abs/2605.28999) / [PDF](https://arxiv.org/pdf/2605.28999)
- **Findings**: Approximately 1% of authentic uploaded resumes contain hidden prompt injections (e.g. white text on white background, zero-width characters, microscopic fonts, off-page layout text). Over 90% of injections avoid explicit imperative trigger words (e.g. "Ignore previous instructions") and instead embed fabricated qualification summaries or prompt-influencing framing. Generic keyword blocklists fail (F1 scores between 0.018 and 0.125).
- **Fix Applied in VIREONIQ**: Phase 7 dual-layer defense: render-versus-extract structural discrepancy detection (flags hidden text and microscopic fonts) + strict structural fencing (candidate text isolated inside inert delimiters with instruction-data channel separation); Phase 13 red-team penetration tests.

### F11. OWASP Top 10 for LLM Applications 2025
- **Source**: OWASP Top 10 for LLM Applications 2025  
  URL: [https://owasp.org/www-project-top-10-for-large-language-model-applications/](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- **Core Vectors**:
  - LLM01: Prompt Injection
  - LLM02: Sensitive Information Disclosure
  - LLM03: Supply Chain Vulnerabilities
  - LLM04: Data and Model Poisoning
  - LLM05: Improper Output Handling
  - LLM06: Excessive Agency
  - LLM07: System Prompt Leakage
  - LLM08: Vector and Embedding Weaknesses
  - LLM09: Misinformation
  - LLM10: Unbounded Consumption
- **Fix Applied in VIREONIQ**: Phase 13 detailed threat matrix mapped in `docs/AI_SECURITY.md`.

### F12. International AI Governance & Legal Frameworks
- **Sources**:
  - *EU AI Act*: High-Risk Systems in Annex III (Recruitment and Employment systems). Note: High-risk transition enforcement timelines are codified for December 2027 (per European Commission rolling guidance and legal analysis).
  - *NYC Local Law 144*: Mandates independent annual bias audits (adverse impact ratio calculation across gender and race/ethnicity) and 10-day advance candidate notices for automated employment decision tools (AEDTs).
  - *India Digital Personal Data Protection (DPDP) Act & Rules*: Notified November 14, 2025; establishing explicit consent notices, verifiable parental consent for minors, purpose limitation, reasonable security safeguards, and mandatory data fiduciary accountability.
- **Fix Applied in VIREONIQ**: Phase 14 compliance readiness engineering in `docs/AI_GOVERNANCE.md`, including audit log pipelines, impact assessment templates, and adverse impact calculation utilities.

---

## C2. Background Algorithmic Methods Referenced

1. **Lexical Matching**: BM25 (Okapi) and TF-IDF with sublinear term-frequency scaling.
2. **Hybrid Fusion**: Reciprocal Rank Fusion (RRF) with constant \( k = 60 \) and convex score combination.
3. **Neural Reranking**: Cross-encoder models computing token-level cross-attention across query and candidate text.
4. **Contrastive Learning**: InfoNCE objective with in-batch hard negative sampling.
5. **Query Augmentation**: Hypothetical Document Embeddings (HyDE) with temperature-controlled query generation.
6. **Calibration & Uncertainty**: Expected Calibration Error (ECE), Brier Score, and Conformal Prediction risk-coverage bounds.
7. **Explainability**: Feature attribution via SHAP / Integrated Gradients and structured natural language rationales with verbatim citation spans.

---

## C3. Open Empirical Gaps and Engineering Mitigations

1. **Hiring Outcome Causality**: Algorithmic scoring does not prove real-world employee performance or job retention; VIREONIQ explicitly labels all scores as qualification alignment indicators, forbidding unverified claims of guaranteed job placement.
2. **Indian Talent Data Scarcity**: Synthetic data generation paired with human validation is required for vernacular language assessment; all synthetic data must be explicitly flagged and versioned.
3. **Minor Protection**: Features designed for high school or early-career students require explicit parental consent workflows and restricted data retention schedules under DPDP requirements.
