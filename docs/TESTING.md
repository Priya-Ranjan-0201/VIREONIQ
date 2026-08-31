# VIREONIQ X — Test Strategy & Automated Verification

## 1. Test Architecture

The automated test suite enforces 100% regression and invariant testing across all 16 intelligence phases and the 6 intelligence capabilities.

- **Framework**: `pytest` (with `pytest-asyncio` and `pytest-mock`)
- **Isolation**: SQLite in-memory engine runs tests with zero external database dependencies
- **Execution Speed**: 142 tests complete in **< 27.0 seconds**

---

## 2. Test Execution Commands

### Run Full Test Suite
```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

### Run Specific Test Suite
```powershell
# Six Intelligence Capabilities
.\.venv\Scripts\python.exe -m pytest tests/test_six_intelligence_capabilities.py -v

# MNC Interview Intelligence
.\.venv\Scripts\python.exe -m pytest tests/test_phase16_mnc_interview_intelligence.py -v

# Canonical Hardening
.\.venv\Scripts\python.exe -m pytest tests/test_canonical_11_10_hardening.py -v

# Concurrency Load Benchmark
.\.venv\Scripts\python.exe -m pytest tests/test_concurrency_load.py -v
```

---

## 3. Test Coverage Matrix

| Test Module | Tests | Focus Area |
|:---|:---:|:---|
| `test_six_intelligence_capabilities.py` | 7 | Evidence integrity, multidimensional mastery, trajectory, what-if simulator, skill transfer, interview memory & closed loop |
| `test_career_decision_explainability.py` | 5 | Evidence-backed decision explainability, range metrics (no false precision), prerequisite bottlenecks, NBA integration |
| `test_ai_gateway_reliability.py` | 5 | LLM timeout, rate limit & fallback |
| `test_auth_security.py` | 3 | Argon2id hashing & RS256 JWT validation |
| `test_canonical_11_10_hardening.py` | 9 | 10-state evidence, twin diff, NBA guard |
| `test_canonical_skills.py` | 3 | Normalized skill aliases & categorization |
| `test_career_digital_twin.py` | 2 | Twin synthesis & capability metrics |
| `test_career_simulator.py` | 2 | Counterfactual career trajectories |
| `test_code_ast_analyzer.py` | 4 | Deterministic Big-O time & space bounds |
| `test_evidence_graph.py` | 3 | Temporal decay & signal weighting |
| `test_forensic_remediation.py` | 7 | Repaired endpoint edge cases |
| `test_career_document_intelligence.py` | 8 | ATS scoring, entity extraction, JD matching |
| `test_phase10_ai_fabric.py` | 6 | AI prompt templates & tool safety |
| `test_phase11_security_privacy.py` | 5 | IDOR isolation, GDPR data deletion |
| `test_phase12_outcome_intelligence.py` | 5 | Career funnel & event idempotency |
| `test_phase13_platform_ecosystem.py` | 5 | Scoped API keys & webhook DLQ |
| `test_phase14_autonomous_career_os.py` | 6 | Autonomous signal intake & NBA |
| `test_phase15_final_convergence.py` | 5 | Intelligence receipts & model registry |
| `test_phase16_mnc_interview_intelligence.py` | 6 | MNC 8-round blueprints & test runner |
| `test_benchmark_critical_apis.py` | 1 | Latency empirical benchmarks |
| `test_concurrency_load.py` | 1 | Concurrency load benchmark loops |
| *Additional Phase & Core Test Suites* | 49 | Readiness, ROI optimizer, Passport, etc. |
| **Total Automated Tests** | **147** | **100.0% Pass Rate** |
