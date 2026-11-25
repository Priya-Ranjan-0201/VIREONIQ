# VIREONIQ Data Catalog & Ingestion Governance

This document establishes the data catalog, provenance records, labeling protocols, synthetic generation guidelines, and privacy rules for all datasets utilized across VIREONIQ.

---

## 1. Data Catalog & Taxonomy Manifest

| Dataset / Corpus | Source / Provider | License | Version | Format / Size | Language(s) | Platform Purpose & Scope |
|---|---|---|---|---|---|---|
| **ESCO Skill & Occupation Taxonomy** | European Commission | Open Data (ODbL) | v1.1.1 | JSON/CSV (~3,000 skills, ~14,000 concepts) | Multilingual (EN, HI, ES, FR, DE) | Canonical skill normalization, hierarchy traversal, and prerequisite skill mapping. |
| **O*NET Content Model** | US Department of Labor | CC BY 4.0 | 28.0 | Tabular / SQL (~1,000 occupations) | English | Work activities, generalized abilities, and task importance weights. |
| **TalentCLEF Benchmark (Evaluation)** | CLEF / arXiv:2606.31692 | Research Open Access | 2026 | JSONL (~5,000 pairs) | English | Benchmark baseline for hybrid retrieval and rank-fusion validation. |
| **Synthetic Candidate Gold Fixtures** | VIREONIQ Internal Seed Generator | Proprietary (Test Only) | v2.1 | JSON (~250 synthetic profiles) | English, Hindi (transliterated & Devanagari) | Offline unit testing, entity-split validation, and CI determinism. |

---

## 2. Evidence Ontology & Labeling Protocol

To prevent binary qualification artifacts and avoid treating unstated attributes as negative signals (F2: Systematized Review of AI Recruitment Systems):

### 2.1 Three-Valued Verification State
- **`SUPPORTED`**: The candidate document contains explicit, verifiable, uncontradicted evidence demonstrating the competency or requirement with cited source spans.
- **`CONTRADICTED`**: The document contains explicit evidence demonstrating a factual contradiction or failure of a mandatory prerequisite (e.g. graduation year mismatch, licensing requirement absence).
- **`UNKNOWN`**: The document does not mention or provide evidence for the requirement. **Missing evidence is NEVER scored as negative**. The system surfaces an explicit "Information Needed" inquiry rather than penalizing candidate scores.

### 2.2 Human Annotation & Adjudication Protocol
1. **Independent Dual Annotation**: Any human-labeled evaluation split is scored by at least two independent annotators following standardized rubric criteria.
2. **Inter-Annotator Agreement Reporting**: Agreement must be measured and reported via Cohen's Kappa ($\kappa$) for nominal categories or Krippendorff's Alpha ($\alpha$) for ordinal/interval ratings. Evaluation sets with $\kappa < 0.65$ are marked unstable and sent for guideline refinement.
3. **Adjudication Process**: Inter-annotator discrepancies are resolved by a senior staff reviewer, with rationale and adjudication deltas recorded in the audit log.

---

## 3. Synthetic Data Policy & Generation Guardrails

1. **Explicit Tagging**: All synthetic data is strictly labeled with `is_synthetic: true` in metadata schemas and data fixtures.
2. **Seeded Determinism**: Synthetic generators must accept an explicit `seed` parameter (default `42`) to guarantee 100% reproducible test generation.
3. **Non-Exclusive Evaluator Rule**: No production model, accuracy claim, or Model Gate sign-off may rely exclusively on synthetic data. Synthetic data must always be corroborated by human gold calibration sets or established open benchmark splits.

---

## 4. PII Redaction & Data Sanitization Rules

Before candidate resumes or feedback are submitted to vector embeddings, logging outputs, or external LLM providers:
1. **Mandatory Redaction**: Email addresses, phone numbers, physical residential addresses, national identification numbers (Aadhaar, SSN), and direct URLs to personal social profiles must be masked with standardized tokens (`[EMAIL_REDACTED]`, `[PHONE_REDACTED]`, `[GOV_ID_REDACTED]`, `[ADDRESS_REDACTED]`).
2. **Redaction Quality Targets**: Redaction recall must meet or exceed 98% on labeled PII evaluation benchmarks (`core/pii_redactor.py`).
3. **Audit Logging**: Raw unredacted candidate text is never persisted in application logs (`SecurityAuditLog` or `structlog`).
