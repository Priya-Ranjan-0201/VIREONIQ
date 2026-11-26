# Model Card: ATS Compatibility Scorer

- **Component ID**: `ats_compatibility_scorer`
- **Status**: Shipped (Deterministic Heuristic + AST/Section Rubric)
- **Evaluation Unit**: Single candidate resume document (with optional target skill keyword list)

## 1. Intended Use & Scope
- Evaluates structural completeness (Summary, Experience, Education, Projects), skill keyword coverage, quantified impact phrasing, and formatting readability on a `[0, 100]` scale.
- Provides actionable remediation items for candidates editing their own resumes.

## 2. Out-of-Scope Use
- **Must NOT** be used as an automated rejection gate or autonomous recruiter decision tool without human review.
- Scores do **not** predict real hiring outcomes or offer probabilities (no longitudinal hiring labels exist).

## 3. Data & Baselines
- Evaluated against deterministic regression fixtures (`backend/tests/test_scoring_properties.py`) and formatting-perturbation suites (`backend/eval/robustness.py`).
- Monotonicity and range bounds verified via Hypothesis/property tests.

## 4. Metrics & Invariants
- Bounded output: `0 <= score <= 100`.
- Determinism: variance `0.0` across repeated runs.
- Monotonicity: adding relevant matching experience or required keywords never decreases score.
- Formatting invariance: whitespace and markdown bullet differences stay within `<= 0.05` normalized delta.

## 5. Fairness, Privacy & Limitations
- No demographic, age, gender, or school-prestige features are read by the scorer; matched-pair name swaps produce identical scores.
- Pre-screening relies on `PIIRedactor` (`backend/core/pii_redactor.py`) before logging or downstream LLM feedback.
- Limitation: Purely lexical/structural heuristic; cannot infer semantic equivalence for novel aliases unless mapped in the canonical skill dictionary.
