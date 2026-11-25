# VIREONIQ — Test Strategy & Automated Verification

## 1. Test Architecture

- **Backend**: `pytest` with `pytest-asyncio` and `pytest-cov` (`backend/pytest.ini` configures `asyncio_mode = auto` and excludes `benchmark` tests by default via `addopts = -m "not benchmark"`).
  - **Isolation**: `backend/tests/conftest.py` runs tests against an in-memory SQLite async engine (`aiosqlite`), with Redis falling back to `SafeRedis` in-memory degradation and Qdrant falling back to `MockQdrantClient` / keyword matching when external services are offline.
  - **Inventory**: `52` `test_*.py` modules containing **188** standard unit/integration/WebSocket tests plus **2** `@pytest.mark.benchmark` suites (`test_benchmark_critical_apis.py` and `test_concurrency_load.py`), totaling **190 passing automated tests**.
  - **Statement Coverage**: **59%** overall (`16,062` statements, `6,589` missed) across `api`, `core`, `crud`, `db`, `schemas`, `services`, `workers`, and `eval`.
- **Frontend**: `vitest` (`vitest.config.ts`) with `jsdom` and `@testing-library/react` (`frontend/src/test/setup.ts`).
  - **Inventory**: `7` test files (**18** unit/component tests) covering auth store & dev-only `mockAuth` gating, `codeStore`, `gapStore`, Axios auth/401 interceptors, `LoginPage`, `RegisterPage`, and `I18nManager` (English + Hindi localized strings, number formatting, and abstention banners).
  - **Typecheck & Lint**: TypeScript `"strict": true` (`tsc -p tsconfig.app.json --noEmit`, 0 errors), ESLint (0 errors, 28 fast-refresh warnings), Vite production build passing.

> **Note**: In-memory test runs do not replace live integration testing against PostgreSQL 16, Redis 7, MongoDB 7, Qdrant, Celery workers, Judge0, or live LLM APIs. See [docs/KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md).

---

## 2. Test Execution Commands

### Backend
```powershell
cd backend

# Lint and strict bug-class typecheck (0 errors across 318 source files)
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy .

# Standard unit, API, security, and WebSocket test suite (188 tests)
.\.venv\Scripts\python.exe -m pytest tests/ -q

# Coverage report across backend packages (59% statement coverage)
.\.venv\Scripts\python.exe -m pytest tests/ -q --cov=api --cov=core --cov=crud --cov=db --cov=schemas --cov=services --cov=workers --cov=eval --cov-report=term-missing

# Benchmark tests (2 tests, excluded by default pytest.ini addopts)
.\.venv\Scripts\python.exe -m pytest -m benchmark -v
```

### Frontend
```powershell
cd frontend
npm run lint       # ESLint (0 errors, 28 warnings)
npm run typecheck  # tsc -p tsconfig.app.json --noEmit with strict: true (0 errors)
npm test           # Vitest unit/component suite (7 files, 18 tests)
npm run build      # Production bundle (dist/)
```

---

## 3. Selected Backend Test Suites (Verified Inventory)

| Test Module | Tests | Focus Area |
|:---|---:|:---|
| `test_career_document_intelligence.py` | 10 | ATS scoring, entity extraction, JD matching |
| `test_canonical_11_10_hardening.py` | 9 | 10-state evidence, twin diff, NBA guard |
| `test_security_hardening.py` | 9 | Production config fail-closed validation, RBAC, IDOR, payments, Redis TTL, sandbox, model supply chain, upload magic bytes |
| `test_six_intelligence_capabilities.py` | 8 | Evidence integrity, mastery, trajectory, simulator, skill transfer, memory |
| `test_forensic_remediation.py` | 7 | Repaired endpoint edge cases |
| `test_career_decision_explainability.py` | 6 | Evidence-backed decision explanations, range metrics, NBA integration |
| `test_phase4_and_ws_coverage.py` | 6 | Auth `/me`/`logout`, HMAC payment verification, privacy governance, DB-backed analytics/gamification/observability, WebSockets, plagiarism fallback |
| `test_phase10_ai_fabric.py` | 6 | AI prompt templates & tool safety |
| `test_phase14_autonomous_career_os.py` | 6 | Autonomous signal intake, goal drift, Level 3 guard |
| `test_phase16_mnc_interview_intelligence.py` | 6 | MNC interview blueprints & test runner |
| `test_data_foundation_and_eval.py` | 6 | Entity-disjoint splits, temporal splits, retrieval/calibration metrics, PII redaction recall, formatting robustness, evaluation harness |
| `test_ai_gateway_reliability.py` | 5 | LLM timeout, rate limit & fallback |
| `test_nlp_retrieval_and_defense.py` | 4 | Zero-width steganography, data fencing, 3-valued ontology (non-negative unknown), BM25 + dense RRF |
| `test_rag_and_model_gate.py` | 4 | RAG citation extraction, evidence abstention, Model Gate 8-point checklist verification |
| `test_responsible_ai_and_governance.py` | 4 | Dual validation, illusion of neutrality detection, autonomy agency guard, reviewer telemetry |
| `test_scoring_properties.py` | 3 | Scoring invariants (boundedness, monotonicity, determinism) |
| `test_benchmark_critical_apis.py` | 1 | Micro-benchmark for ATS and readiness APIs (`benchmark` marker) |
| `test_concurrency_load.py` | 1 | Controlled async concurrency throughput (`benchmark` marker) |
