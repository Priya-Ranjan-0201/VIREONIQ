# Model Card: ATS Compatibility Scorer

## Model Details
- **Component**: Deterministic ATS Compatibility Scorer (`backend/services/ats_scorer.py` & `backend/tests/test_scoring_properties.py`)
- **Version / Status**: `v1.0` — **Shipped**
- **Evaluation Unit**: Single resume document (text/PDF/DOCX extracted payload) paired against optional canonical skill list.

## Intended Use & Out-of-Scope Use
- **Intended Use**: Diagnostic structural & keyword compatibility feedback for candidates preparing resumes.
- **Out-of-Scope Use**: Must **never** be used as an automated hiring/rejection gate or presented as a guarantee of placement outcomes.

## Data & Privacy Notes
- Evaluates only extracted candidate text; PII is masked before logging or LLM routing (`backend/core/pii_redactor.py`).
- Missing sections or unparseable files produce `UNKNOWN` / flagged errors rather than silent negative scoring.

## Metrics vs Baseline & Robustness
- Property tests verify range boundedness `[0, 100]`, monotonicity when relevant verified skills increase, and strict determinism (`repeatability_variance == 0.0`).
- Evaluated for formatting invariance (stripping markdown/bold artifacts yields score within tolerance).

## Limitations & Failure Modes
- Heuristic section matching may miss non-standard creative resume headers; does not measure real employer callback outcomes.
