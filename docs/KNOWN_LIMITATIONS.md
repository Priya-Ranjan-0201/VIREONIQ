# Known Limitations & Consolidation Proposals

This document records verified architectural debt, remaining placeholders/simulations, external runtime dependencies, and pending decisions intentionally deferred for explicit repository owner approval.

---

## 1. Decisions Owed (Not Changed Unilaterally)

1. **Repository License Conflict (`LICENSE` vs docs)**
   - `LICENSE` contains a Proprietary & Strict Source-Available license.
   - `README.md` previously displayed an MIT badge and claim; the conflicting badge/claim was removed from `README.md` and `LICENSE` was left untouched pending explicit owner direction.
2. **JWT & Password Hashing Libraries (`python-jose` / `passlib`)**
   - `backend/requirements.txt` upgrades `python-jose[cryptography]==3.5.0`, which still carries `PYSEC-2026-4298` (no upstream fix release in `python-jose`).
   - `passlib==1.7.4` is unmaintained upstream and emits `argon2.__version__` deprecation warnings under newer `argon2-cffi`.
   - Migrating to `PyJWT[crypto]` and `pwdlib[argon2]` (or `argon2-cffi` directly) is recommended but held pending owner sign-off.
3. **Overlapping / Legacy Service Modules**
   - No modules or public routes were deleted during hardening; consolidation proposals with verified callers are documented in Section 3 below.

---

## 2. Remaining Placeholders, Simulations & Schema Gaps

- **Google Calendar Sync (`backend/api/api_v1/endpoints/calendar.py`)**: `POST /api/v1/calendar/sync` returns `"Event synced to Google Calendar (Simulated)"` and does not invoke the Google Calendar API.
- **Parent Digest (`backend/api/api_v1/endpoints/parent.py`)**: `GET /api/v1/parent/digest` returns static placeholder values (`overall_placement_readiness`, `completed_interviews_count`, `recent_activity`) rather than aggregating real student DB telemetry.
- **Code Execution Sandbox (`backend/services/code/judge0_provider.py`, `backend/services/code_execution_service.py`)**: Fails closed cleanly (`Sandbox Unavailable`, `status.id = 13`, `passed = False`) whenever `JUDGE0_API_URL` is unset or unreachable. No local unsandboxed Python fallback executes anymore; real execution requires a configured Judge0 / Piston sandbox instance.
- **Plagiarism Semantic Search (`backend/services/plagiarism_guard.py`)**: Uses lazy `SentenceTransformer` + Qdrant when reachable, falling back to token-Jaccard matching against `KNOWN_ANSWERS_SEEDS` when Qdrant or embedding weights are unavailable.
- **Platform API Key Foreign Key vs Endpoint Tenant ID (`backend/db/models.py`, `backend/api/api_v1/endpoints/platform_developer.py`)**: `PlatformApiKey.tenant_id` defines a foreign key to `recruiter_organizations.id`, while `platform_developer.py` currently scopes `PlatformApiKey` queries and inserts by `current_user.id`. This succeeds on SQLite (where `PRAGMA foreign_keys` defaults off in tests) but will raise a foreign-key constraint violation on PostgreSQL unless `platform_developer.py` resolves or provisions the caller's `RecruiterOrganization.id`.
- **Smart Apply Tracker Storage (`frontend/src/pages/jobs/SmartApplyTracker.tsx`)**: Persists job application tracking cards locally in browser `localStorage` rather than a backend persistence table.
- **SQLAlchemy 1.x ORM Annotations (`backend/db/models.py`)**: Models use untyped `Column(...)` descriptors instead of SQLAlchemy 2.0 `Mapped[...]`. In `backend/pyproject.toml`, `mypy` checks `core.*`, `schemas.*`, and `db.*` with zero disabled error codes, and disables SQLAlchemy `Column[T]` mismatch noise codes on ORM-consuming packages while keeping `call-arg`, `attr-defined`, `name-defined`, `misc`, `dict-item`, and `syntax` strictly enforced everywhere.
- **Live External Stacks**: Postgres 16, Redis 7, MongoDB, Qdrant, Celery workers, and third-party LLM providers (`OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `NVIDIA_NIM_API_KEY`, `DEEPSEEK_API_KEY`) were not started or exercised against live external services in local offline verification (`pytest` uses in-memory SQLite + `SafeRedis` in-memory fallback + `MockQdrantClient`).

---

## 3. Overlapping Module Consolidation Proposals (Pending Approval)

The following overlapping modules remain active with distinct callers and should be reviewed before deprecating the legacy module in each group:

| Domain | Legacy / Earlier Module(s) | Newer / Target Module | Observed Callers Today | Proposed Consolidation |
| :--- | :--- | :--- | :--- | :--- |
| Career Simulation | `services/career_simulator_service.py` | `services/career_simulation_service.py` | `career_simulator_service`: `tests/test_career_simulator.py`<br>`career_simulation_service`: `api/api_v1/endpoints/career_simulator.py`, `tests/test_phase9_career_simulator.py` | Migrate `test_career_simulator.py` onto `career_simulation_service.py` and deprecate `career_simulator_service.py`. |
| Skill Gap Analysis | `services/gap_service.py`, `services/gap_engine.py`, `services/intelligence/gap_analysis.py` | `services/gap_intelligence_service.py` | `gap_service`/`gap_engine`: `api/api_v1/endpoints/gap.py`<br>`GapAnalysisEngine`: `services/analytics_service.py`<br>`gap_intelligence_service`: `api/api_v1/endpoints/roi_gaps.py`, `services/counterfactual_simulation_service.py`, `services/roi_career_optimizer_service.py`, `tests/test_phase3_synthetic_validation.py` | Route `/api/v1/gap` through `gap_intelligence_service` while keeping response schema compatible. |
| Resume Parsing & Scoring | `services/resume_service.py`, `services/resume_parser.py`, `services/resume_scorer.py` | `services/resume_builder_service.py` | `resume_service`/`resume_scorer`: `api/api_v1/endpoints/resume.py`, `tests/test_career_document_intelligence.py`, `tests/test_hrcv_integrated_capabilities.py`<br>`resume_builder_service`: `api/api_v1/endpoints/resume_builder.py`, `api/api_v1/endpoints/resume.py` (`rewrite_resume_section`) | Share a single canonical parser/scorer module (`resume_parser.py` + `resume_scorer.py`) called by both `/resume` and `/resume-builder`. |
| Credential Issuance | `services/credential_service.py` | `services/credential_issuance_service.py` | `credential_service`: `tests/test_talent_passport.py`<br>`credential_issuance_service`: `api/api_v1/endpoints/credentials.py`, `tests/test_canonical_11_10_hardening.py`, `tests/test_phase6_*`, `tests/test_security_hardening.py`, `tests/test_hrcv_integrated_capabilities.py` | Point `get_talent_passport_data` callers to `talent_passport_service.py` / `credential_issuance_service.py` and retire `credential_service.py`. |
| Prescriptive Interventions | `services/intervention_service.py` | `services/career_intervention_engine.py` | `intervention_service`: `api/api_v1/endpoints/missions.py`, `tests/test_prescriptive_interventions.py`<br>`career_intervention_engine`: `api/api_v1/endpoints/interventions.py`, `api/api_v1/endpoints/market.py`, `services/career_simulation_service.py`, Phase 5/6 tests | Merge `missions.py` intervention generation onto `career_intervention_engine.py`. |
| Analytics & Outcomes | `services/analytics_service.py` | `services/outcome_intelligence_service.py` | `analytics_service`: `api/api_v1/endpoints/analytics.py`, `services/report_service.py`<br>`outcome_intelligence_service`: `api/api_v1/endpoints/outcomes_analytics.py`, `tests/test_phase12_outcome_intelligence.py` | Keep `analytics_service.py` for user dashboard stats + GPS calculation and `outcome_intelligence_service.py` for funnel/progression events without duplicate metric definitions. |
| Code Sandbox Fallback | `services/code/judge0_mock.py` | `services/code/judge0_provider.py`, `services/code_execution_service.py` | Zero runtime callers (`judge0_mock.py` bypassed after fail-closed Phase 2 hardening) | Safe candidate for removal once owner approves deleting `judge0_mock.py`. |
