# VIREONIQ — Test Strategy & Automated Verification

## 1. Test Architecture

- **Backend**: `pytest` with `pytest-asyncio` and `pytest-cov` (`backend/pytest.ini` configures `asyncio_mode = auto` and excludes `benchmark` tests by default via `addopts = -m "not benchmark"`).
  - **Isolation**: `backend/tests/conftest.py` runs tests against an in-memory SQLite async engine (`aiosqlite`), with Redis falling back to `SafeRedis` in-memory degradation and Qdrant falling back to `MockQdrantClient` / keyword matching when external services are offline.
  - **Inventory**: `49` `test_*.py` modules containing **165** standard unit/integration/WebSocket tests plus **2** `@pytest.mark.benchmark` suites (`test_benchmark_critical_apis.py` and `test_concurrency_load.py`), plus `test_hrcv_integrated_capabilities.py` integration checks.
- **Frontend**: `vitest` (`vitest.config.ts`) with `jsdom` and `@testing-library/react` (`frontend/src/test/setup.ts`).
  - **Inventory**: `6` test files (`14` unit/component tests) covering auth store & dev-only `mockAuth` gating, `codeStore`, `gapStore`, Axios auth/401 interceptors, `LoginPage`, and `RegisterPage`.

> **Note**: In-memory test runs do not replace live integration testing against PostgreSQL 16, Redis 7, MongoDB 7, Qdrant, Celery workers, Judge0, or live LLM APIs. See [docs/KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md).

---

## 2. Test Execution Commands

### Backend
```powershell
cd backend

# Lint and strict bug-class typecheck
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy .

# Standard unit, API, security, and WebSocket test suite (165 tests)
.\.venv\Scripts\python.exe -m pytest tests/ -q

# Coverage report across backend packages
.\.venv\Scripts\python.exe -m pytest tests/ -q --cov=api --cov=core --cov=crud --cov=db --cov=schemas --cov=services --cov=workers --cov-report=term-missing

# Benchmark tests (2 tests, excluded by default pytest.ini addopts)
.\.venv\Scripts\python.exe -m pytest -m benchmark -v
```

### Frontend
```powershell
cd frontend
npm run lint
npm run typecheck
npm test
npm run build
```

---

## 3. Selected Backend Test Suites (Verified Inventory)

| Test Module | Tests | Focus Area |
|:---|---:|:---|
| `test_career_document_intelligence.py` | 10 | ATS scoring, entity extraction, JD matching |
| `test_canonical_11_10_hardening.py` | 9 | 10-state evidence, twin diff, NBA guard |
| `test_six_intelligence_capabilities.py` | 8 | Evidence integrity, mastery, trajectory, simulator, skill transfer, memory |
| `test_forensic_remediation.py` | 7 | Repaired endpoint edge cases |
| `test_security_hardening.py` | 7 | Production config fail-closed validation, RBAC, IDOR, payments, Redis TTL, sandbox |
| `test_career_decision_explainability.py` | 6 | Evidence-backed decision explanations, range metrics, NBA integration |
| `test_phase4_and_ws_coverage.py` | 6 | Auth `/me`/`logout`, HMAC payment verification, privacy governance, DB-backed analytics/gamification/observability, WebSockets, plagiarism fallback |
| `test_phase10_ai_fabric.py` | 6 | AI prompt templates & tool safety |
| `test_phase14_autonomous_career_os.py` | 6 | Autonomous signal intake, goal drift, Level 3 guard |
| `test_phase16_mnc_interview_intelligence.py` | 6 | MNC interview blueprints & test runner |
| `test_ai_gateway_reliability.py` | 5 | LLM timeout, rate limit & fallback |
| `test_phase11_security_privacy.py` | 5 | Tenant isolation, privacy opt-out, export/delete, fairness parity audit, audit logging |
| `test_phase12_outcome_intelligence.py` | 5 | Career funnel & event idempotency |
| `test_phase13_platform_ecosystem.py` | 5 | Scoped API keys & webhook DLQ |
| `test_phase15_final_convergence.py` | 5 | Intelligence receipts, model registry, convergence gates |
| `test_phase8_workforce_intelligence.py` | 5 | Workforce capability matrix & simulations |
| `test_phase9_career_simulator.py` | 5 | Counterfactual simulation comparisons |
| `test_phase5_intervention_engine.py` | 4 | Prescriptive intervention generation |
| `test_code_ast_analyzer.py` | 4 | Deterministic Big-O AST analysis |
| `test_benchmark_critical_apis.py` | 1 | Latency benchmark (`-m benchmark`) |
| `test_concurrency_load.py` | 1 | Concurrency load benchmark (`-m benchmark`) |
| *Remaining 28 test modules* | 51 | Auth, readiness, ROI optimizer, passport, skills, mentoring, etc. |
| **Total Executed Pytest Cases** | **167** | **165 standard + 2 benchmark tests across 49 files** |
