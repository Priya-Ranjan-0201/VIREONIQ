# Model Card: Career Trajectory Simulator (Experimental)

- **Component ID**: `career_trajectory_simulator`
- **Status**: **EXPERIMENTAL** (Flagged Behind Experimental Controls; Excluded from Headline Claims)
- **Evaluation Unit**: Multi-step role trajectory / scenario forecast

## 1. Intended Use & Out-of-Scope
- Scenario exploration tool illustrating possible skill transitions and time-to-role horizons under explicit modeling assumptions.
- **Strictly Out-of-Scope**: Cannot predict actual individual promotion odds, placement probabilities, or causal career earnings.

## 2. Why This Component Is Experimental (Model Gate Status)
- **Fails Gate Item 3/8 (Real Longitudinal Data)**: Trained/parameterized without proprietary longitudinal career-graph outcomes (cf. CAPER, `docs/RESEARCH.md` F9).
- **Fails Causal Estimand Check**: Scenario deltas are parametric heuristics, not causal uplift estimates with confoundedness adjustments.
- Skill decay uses a documented assumption (`F(t) = 100 * e^(-0.04t)`) rather than an empirically fitted decay curve.

## 3. UI & Documentation Framing
- Explicitly labeled as scenario simulation / experimental in `docs/KNOWN_LIMITATIONS.md` and `docs/IMPROVEMENT_REPORT.md`.
