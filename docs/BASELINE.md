# VIREONIQ Baseline Audit Measurements (Phase 0)

> **Branch**: `hardening/full-audit` (branched from `origin/main` at commit `1a77f80`)  
> **Measurement Environment**: Windows 11, Python `3.12.10`, Node `v26.13.1`, `npm 12.0.2`, Docker `29.9.3` (PostgreSQL/Redis/MongoDB/Qdrant daemons not running locally in this baseline).  
> **Policy**: Zero source code modifications preceded these measurements. Every figure below is taken directly from tool output in this session.

---

## 1. Repository Inventory

| Metric | Observed Value | Notes / Scope |
|---|---:|---|
| Backend Python files | 302 | Excluding `.venv`, `__pycache__` |
| Backend Python LOC | 48,528 | Line count across 302 `.py` files |
| Backend service modules (`backend/services/`) | 123 | 102 top-level `.py` files + submodules (excluding `__init__.py`) |
| Backend API modules (`backend/api/`) | 77 | 75 endpoint modules in `backend/api/api_v1/endpoints/` (excluding `__init__.py`) |
| Backend test files (`backend/tests/`) | 48 | 47 `test_*.py` files + `conftest.py` (excluding `__init__.py`) |
| `def test_` regex hits in `backend/tests/` | 156 | **150** unique tests + **2** `@pytest.mark.benchmark` tests + **4** fixtures (`test_engine`, `test_user` in `conftest.py`; `test_db` in two test modules) |
| Star-import test duplication | +10 | `test_hrcv_integrated_capabilities.py` does `from tests.test_career_document_intelligence import *` (0 own tests, 10 re-executed) |
| Frontend TS/TSX files (`frontend/src/`) | 117 | `.ts` and `.tsx` |
| Frontend TS/TSX LOC | 38,423 | Line count across 117 files |
| Frontend pages (`frontend/src/pages/`) | 73 | Excluding `index.tsx` |
| Frontend explicit `any` occurrences | 102 | `98` `: any` annotations + `4` `as any` casts |

---

## 2. Backend Verification Baseline

### 2.1 Requirements & Dependencies (`backend/requirements.txt`)
- **Unpinned requirement**: `openai>=1.10.0` (1 of 38 lines).
- **Used in backend code (`import`) but missing from `backend/requirements.txt`**: `aiosqlite`, `pypdf`, `pytest`, `pytest-asyncio`, `PyPDF2` (`api/api_v1/endpoints/syllabus.py:4`).
- **Pinned in `backend/requirements.txt` with 0 direct imports in `backend/`**: `twilio==8.10.0`, `sendgrid==6.11.0`, `langdetect==1.0.9`, `transformers==4.37.2`, `beautifulsoup4==4.12.3`, `zxcvbn==4.4.28`, `bleach==6.1.0`, `scikit-learn==1.4.0` (`argon2-cffi` is used indirectly by `passlib[argon2]`).
- **`pip-audit -r requirements.txt --no-deps --disable-pip -s osv`**: Exits `1` immediately because `openai>=1.10.0` is not pinned to an exact version.
- **OSV batch query (`https://api.osv.dev/v1/querybatch`) against the 37 pinned lines**: **82 known advisories across 9 packages**:
  - `transformers==4.37.2`: 46 advisories
  - `python-multipart==0.0.6`: 18 advisories
  - `python-jose==3.3.0`: 7 advisories (`GHSA-3qf3-8w2g-rqmx`, `GHSA-6c5p-j8vq-pqhj`, `GHSA-cjwg-qfpm-7377`, `PYSEC-2024-232`, `PYSEC-2024-233`, `PYSEC-2025-185`, `PYSEC-2026-4298`) — note even `python-jose==3.5.0` still has 2 advisories (`GHSA-3qf3-8w2g-rqmx`, `PYSEC-2026-4298`)
  - `sentence-transformers==2.3.1`: 2 advisories
  - `qdrant-client==1.7.0`: 2 advisories
  - `sentry-sdk==1.40.0`: 2 advisories
  - `bleach==6.1.0`: 2 advisories
  - `scikit-learn==1.4.0`: 2 advisories
  - `fastapi==0.109.0`: 1 advisory (`PYSEC-2024-38`)

### 2.2 Test Suite Baseline (`pytest.ini` sets `addopts = -m "not benchmark"`)
1. **Global Python 3.12 environment (missing `magic`, `anthropic`, `PyPDF2`)**:
   - `python -m pytest tests/ -v --tb=short`: **6 collection errors** (`test_benchmark_critical_apis.py`, `test_career_decision_explainability.py`, `test_career_document_intelligence.py`, `test_concurrency_load.py`, `test_hrcv_integrated_capabilities.py`, `test_talent_passport.py`), `134 deselected`, exit `1`.
   - Ignoring the 6 collection-broken files: **133 passed, 1 failed** in `7.98s` (`test_mock_llm_generate_json_prompt_lower` fails with `ModuleNotFoundError: No module named 'anthropic'`).
2. **Isolated `.venv` (`--system-site-packages` + `anthropic`, `python-magic-bin`, `pypdf`, `pytest-cov`)**:
   - `pytest tests/`: **3 collection errors** (`test_benchmark_critical_apis.py`, `test_career_decision_explainability.py`, `test_concurrency_load.py`), all caused by `ModuleNotFoundError: No module named 'PyPDF2'` in `api/api_v1/endpoints/syllabus.py:4`.
   - `pytest -m benchmark`: **3 collection errors** (same `PyPDF2` import via `main.py` -> `router.py` -> `syllabus.py`), **0 benchmark tests runnable** until `PyPDF2` import is replaced.
   - Ignoring the 3 `PyPDF2`-blocked files: **155 passed, 1 warning in 36.40s** (representing 145 unique non-benchmark tests + 10 duplicate executions from `test_hrcv_integrated_capabilities.py`).
   - **Statement coverage** (`--cov=api --cov=core --cov=crud --cov=db --cov=schemas --cov=services --cov=workers`): **50% overall** (`11,678` statements, `5,887` missed) in `73.85s`.

### 2.3 Static Analysis & Code Smells (Backend)
- **Ruff (`python -m ruff check . --statistics`)**: **3,627 errors** (`2,414` auto-fixable).
  - Core subset (`E4,E7,E9,F`): **818 errors** (`678` `F401` unused imports, `29` `F541`, `26` `F841`, `21` `E701`, `20` `E402`, `16` `E712`, `12` `E741`, `12` `F811`, `3` `E711`, `1` `F403`).
- **Mypy (`python -m mypy .`)**: Exits `2` on `Duplicate module named "auth"` (`schemas/auth.py` vs `api/api_v1/endpoints/auth.py`).
  - With `--explicit-package-bases --ignore-missing-imports`: **824 errors across 165 files** (302 files checked).
- **Vulture (`vulture . --min-confidence 80`)**: **48** flagged lines.
- **Exception handling & logging (non-test, non-script Python)**:
  - Bare `except:`: **0**
  - Broad `except` (`except Exception` / `except:`): **120** (`38` have no log/raise/print in the next 3 lines; top files: `core/redis.py` 9, `services/resume_parser.py` 8, `services/psychometric.py` 5, `services/resume_builder_service.py` 5).
  - `print()` statements: **11** (`core/config.py` 2, `main.py` 7, `services/parent_digest_service.py` 2).
- **Markers in non-test, non-script Python**: `TODO`: 6 (all inside student starter-code strings in `services/internship_service.py`), `HACK`: 4, `placeholder`: 6, `mock`: 77, `synthetic`: 14, `hardcoded`: 1, `dummy`: 8.

---

## 3. Frontend Verification Baseline

| Check | Command | Exit | Result |
|---|---|---:|---|
| Dependency install | `npm ci` | 0 | 697 added in 2m; install scripts blocked by npm policy for `core-js@3.49.0` and `esbuild@0.21.5` |
| Lint | `npm run lint` (`eslint .`) | 1 | **44 problems**: **16 errors** (`no-empty`, `no-useless-escape`) + **28 warnings** (`react-hooks/exhaustive-deps`, `react-refresh/only-export-components`) |
| Root `tsc` | `npx tsc --noEmit` | 0 | **False green**: root `tsconfig.json` has `"files": []` and `"references"`, so `tsc` without `-b` checks 0 files |
| App `tsc` | `npx tsc -p tsconfig.app.json --noEmit` | 2 | **416 TypeScript errors** (`TS6133`, `TS6196`, `TS1484` etc.) — `"strict"` is not enabled in `tsconfig.app.json` |
| App `tsc --strict` | `npx tsc -p tsconfig.app.json --strict --noEmit` | 2 | **416 TypeScript errors** observed with `tsconfig.app.json` project settings |
| Production build | `npm run build` (`tsc && vite build`) | 0 | Succeeded in `7.27s` **only because `tsc` without `-b` skips typechecking `src/`**; Rollup emitted 7 missing-export warnings (e.g. `LanguageConfig`, `CompanyProfile`, `InternshipTask`) |
| Dependency audit | `npm audit` | 1 | **33 vulnerabilities** (`2` low, `12` moderate, `18` high, `1` critical; includes `axios`, `dompurify`/`jspdf`, `esbuild`/`vite`, `react-router-dom`, `nanoid`, `postcss`, `zod`) |
| Code markers (`frontend/src`) | Custom AST/regex scan | 0 | `any` (colon + `as any`): **102**; `localStorage`: **39**; `sessionStorage`: **8**; empty `catch {}`: **15**; `mock`: **53**; `placeholder`: **125** |

---

## 4. Confirmed Audit Findings & Decision Gates

### Repo Hygiene & Honesty Gaps
1. **License Contradiction (User Decision Owed)**: `README.md` badge & license section claim **MIT**, while `LICENSE` is a **Proprietary & Strict Source-Available Copyright License**. `LICENSE` will NOT be modified without explicit user choice.
2. **Unverified / Contradicted README & Doc Claims**: README claims `153/153_Passing` (`153 passed in 14.82s`), TailwindCSS 3.4 (repo uses `@tailwindcss/vite` 4.3.1 alongside unused `postcss`/`autoprefixer` config), `"95+ Score Guaranteed"`, `"enterprise-grade"`, `"GDPR & CCPA Compliant"`, and exposes `test@example.com` / `password` credentials.
3. **Tracked Runtime Artifacts**: `backend/celerybeat-schedule`, `backend/celerybeat-schedule.db.bak`, `backend/celerybeat-schedule.db.dat`, `backend/celerybeat-schedule.db.dir` are tracked in git, and `.gitignore` does not ignore `celerybeat-schedule*`.
4. **Hardcoded Developer Paths**: `backend/pyproject.toml` and `backend/pyrefly.toml` hardcode `D:/Downloads/VIREONIQ-MERGE/VIREONIQ-X/backend/.venv/...`.
5. **Naming Drift**: `PLACEIQ`, `VIREONIQ`, `VIREONIQ X`, and `HRCV` appear inconsistently across `.env.example`, `alembic.ini` (`placeiq`), `frontend/package.json` (`placeiq-frontend`), `authStore.ts` (`placeiq-auth`), `credential_service.py` (SVG `PLACEIQ`), `global_parity.py` (`placeiq.app`), and `rules.md`.
6. **Silent CI**: `.github/workflows/ci.yml` has a placeholder comment `# Add flake8 or black check here`, runs zero backend tests/linters, and only runs `npm install` + `npm run build` (where `tsc` checks 0 files).

### Confirmed Security & Reliability Risks (To Remediate in Phase 2)
- **Privilege escalation on signup**: `POST /api/v1/auth/register` accepts arbitrary `role_name` (`UserRegisterRequest.role_name`), letting a registrant pick `"Admin"` or `"Recruiter"`; default `"student"` does not even match seeded roles (`User`, `Admin`, `Recruiter`).
- **RCE & fabricated execution in code sandbox**: `backend/services/code/judge0_provider.py` executes untrusted Python directly on the backend host via `sys.executable -c source_code` when `judge0-server:2358` is unreachable and fabricates `"All test suites passed"` for 16 other languages; `code_execution_service.py` also returns fake `passed=True` fallbacks.
- **Client-controlled RBAC bypass**: `POST /api/v1/ai-orchestration/...` accepts `acting_role_name` from the HTTP request body (`ai_tool_registry.py`), allowing privilege impersonation and IDOR, plus broken `calculate_team_capability_coverage(uid, db)` / `uuid.uuid4()` organization calls.
- **Unauthenticated / IDOR / tenant-leak endpoints**:
  - `GET /privacy-security/audit-logs` dumps all users' security logs instead of scoping to `current_user.id` (or requiring Admin).
  - `platform_developer.py` lacks ownership/tenant checks on `/api-keys`, `DELETE /api-keys/{key_id}`, and `/webhooks`.
  - `recruiter_intelligence.py` and `workforce_intelligence.py` auto-provision `RECRUITER_ADMIN` / `ORGANIZATION_ADMIN` for any caller.
  - `referral_economy.py` `/log-outcome/{id}` and `mnc_interview.py` endpoints lack authentication; `matchmaker.py` and `advanced_modes.py` WebSockets lack authentication; `main.py` mounts `/uploads` publicly; `resume_builder.py` uses `get_optional_current_user`.
  - `payments.py` `/verify` skips HMAC signature verification whenever `RAZORPAY_KEY_SECRET` is unset, and does not verify `tx.user_id` or match `plan_id` to transaction amount.
  - `credential_issuance_service.py` mints signed `ASSESSED_COMPETENCY` credentials at a default `score=75.0` even when `SkillEvidence` is absent.
- **Configuration, startup, & cryptography hygiene**:
  - `core/config.py`: hardcoded `SECRET_KEY`, default `password` DB password, `PRIVATE_KEY_PATH` vs `JWT_PRIVATE_KEY_PATH` env mismatch, blocking synchronous 0.3s TCP probe on every `async_database_url` property read with silent fallback to `./placeiq.db` even in production, no production startup validation.
  - `core/security.py`: generates RSA keys on disk at import time (`_ensure_keys_exist()`); naive keyword/substring `check_prompt_injection` blocks `"--"`.
  - `core/redis.py`: permanently sets `_disabled = True` on a single transient error; fallback `setex` ignores TTL.
  - `main.py`: strict `Content-Security-Policy: default-src 'none'; sandbox;` breaks `/docs`/`/redoc`; `remove_trailing_slash` issues HTTP 307 redirects on POST/PUT/DELETE; `global_exception_handler` drops exception details.
  - `crud/crud_user.py`: joins `Profile.user_id == ResumeScore.resume_id` (wrong column -> always 0.0 ATS score) and ignores `allow_recruiter_discovery`.
  - `docker-compose.yml`: unpinned `qdrant/qdrant:latest`, Redis without password, DB ports published on `0.0.0.0`, default weak passwords.
  - `frontend`: `LoginPage.tsx` can fall back to `mockAuth.ts` (`localStorage` offline bypass) on network errors even outside dev builds; `authStore.ts` persists JWT in `localStorage`.

### Overlapping Modules & Non-Destructive Consolidation Plan
Four service pairs overlap and have distinct callers/tests:
1. `career_simulation_service.py` (Phase 9) vs `career_simulator_service.py` (legacy + `tests/test_career_simulator.py`)
2. `credential_issuance_service.py` (Phase 6 HMAC) vs `credential_service.py` (`get_talent_passport_data` + `tests/test_talent_passport.py`)
3. `gap_intelligence_service.py` (Phase 3 evidence-based) vs `gap_engine.py` + `gap_service.py` (`/gap` + `analytics_service.py`)
4. `career_intervention_engine.py` (Phase 5) vs `intervention_service.py` (`/missions/interventions` + `tests/test_prescriptive_interventions.py`)
5. `judge0_mock.py` (0 callers) vs `judge0_provider.py` (`/code`)

Per non-negotiable rules 4 & 7, legacy modules and `python-jose` will NOT be unilaterally deleted or swapped without explicit user sign-off; instead, `docs/BASELINE.md` and `docs/IMPROVEMENT_REPORT.md` document exact callers and concrete migration recommendations.
