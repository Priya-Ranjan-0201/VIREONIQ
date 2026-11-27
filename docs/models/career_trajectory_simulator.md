# Model Card: Career Trajectory & Skill Decay Simulator (Experimental)

> **Status**: **EXPERIMENTAL** — Excluded from headline shipped claims; gated behind explicit UI scenario labels (`docs/KNOWN_LIMITATIONS.md`).

## Model Details
- **Component**: `career_simulator_service.py` & skill decay curve (`F(t) = 100 * e^(-0.04t)`).
- **Evaluation Unit**: Multi-horizon scenario simulation (non-causal).

## Limitations & Failure Modes
- Currently relies on heuristic transition rules and fixed exponential decay assumptions rather than longitudinal real-world hiring outcome data.
- Causal claims and "placement probability" framing are explicitly prohibited per Master Prompt v2 Model Gate item 12.
- Requires longitudinal consented dataset validation and temporal backtesting (Part C, F9) before promotion out of experimental status.
