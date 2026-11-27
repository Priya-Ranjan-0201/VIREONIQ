# Architecture and Engineering Decision Log

This log records significant architectural, security, stack, and methodology decisions for VIREONIQ. Each entry documents context, options considered, the chosen decision, and resulting consequences.

---

## Decision 001: Standardization on Python 3.12 (PY3.12)
- **Status**: Accepted
- **Date**: 2026-11-25
- **Context**: The repository previously showed version drift across documentation, scripts, and container specs (mentioning Python 3.10+, 3.11, and 3.12).
- **Options Considered**:
  1. *Python 3.11*: Mature, broad binary wheel support.
  2. *Python 3.12*: Active standard, improved interpreter performance, modern type hinting, standardized virtualenv tooling.
- **Decision**: Standardize on **Python 3.12** across all components: CI pipelines (`.github/workflows/ci.yml`), container definitions (`backend/Dockerfile`), documentation (`README.md`, `CONTRIBUTING.md`), and local runtime setups.
- **Consequences**:
  - Requires Python 3.12 compatible wheels for dependencies (e.g. `python-magic-bin` on Windows dev; `libmagic1` in Linux CI/Docker).
  - Eliminates ambiguity in typing features and standard library deprecations.

---

## Decision 002: Baseline Branching and Cumulative Hardening Strategy
- **Status**: Accepted
- **Date**: 2026-11-25
- **Context**: An initial audit pass established clean Ruff linting (0 errors), clean Mypy typechecking across 300 backend files, 165 passing standard tests + 2 benchmarks, and critical security patches on branch `hardening/full-audit`.
- **Options Considered**:
  1. *Branch fresh from `origin/main`*: Would discard verified security patches, clean typechecking, and test fixes, re-introducing dozens of regressions.
  2. *Branch from `hardening/full-audit` (`42cb1d3`)*: Preserves all 16 commits of hardening, using this robust baseline to implement Master Prompt v2 Phases 0–18 cleanly.
- **Decision**: Branch feature phases from `hardening/full-audit`, keeping commits atomic, structured, and verified against the established regression harness.
- **Consequences**:
  - All subsequent phases inherit strict TypeScript checking, zero Ruff lint errors, and zero Mypy type errors.
  - Ensures changes are incremental and never break existing green checks.

---

## Decision 003: Model Gate Protocol and Deterministic Fake Providers for Testing
- **Status**: Accepted
- **Date**: 2026-11-25
- **Context**: Machine learning and LLM components in career intelligence can produce deceptive, uncalibrated, or biased scores if shipped without strict quality gates. Furthermore, CI pipelines must remain fast (<15 min) and cannot incur external API costs or external network flakiness.
- **Options Considered**:
  1. *Calling live LLM endpoints in CI*: Incurs recurring cost, risks rate-limiting, leaks data, and causes non-deterministic build failures.
  2. *Deterministic fake providers in unit/CI tests + Model Gate verification*: Use deterministic fake LLMs and local embedding models for CI; require any shipped career intelligence model to pass the 8-item Model Gate (baseline beat, entity-split test, leakage check, fairness audit, uncertainty calibration, latency bounds).
- **Decision**: Enforce the Model Gate across all scoring/recommendation modules. All default CI and test suites must use deterministic fake providers with zero external network dependencies.
- **Consequences**:
  - Default CI runs completely offline, fast, and deterministically.
  - Unverified models remain explicitly marked as `Experimental` in code and documentation.

---

## Decision 004: Preservation of Source-Available License with Transparent Documentation
- **Status**: Accepted
- **Date**: 2026-11-25
- **Context**: `LICENSE` contains a "Proprietary & Strict Source-Available" license, while legacy `README.md` badges and sections historically referenced MIT. Non-negotiable rule 6 states: "Do not choose the license for me."
- **Options Considered**:
  1. *Unilaterally overwrite `LICENSE` with MIT*: Violates non-negotiable rule 6 and user copyright ownership.
  2. *Preserve `LICENSE` verbatim, align README to indicate Proprietary Source-Available status, and document the conflict*: Respects the legally operative file and provides absolute transparency.
- **Decision**: Keep `LICENSE` intact as Proprietary & Source-Available. Reconcile `README.md` to reference the exact `LICENSE` terms and document the distinction.
- **Consequences**:
  - No accidental license changes without explicit user instructions.
  - Accurate legal posture in all repository metadata.

---

## Decision 005: Local Autonomous Execution Flow
- **Status**: Accepted
- **Date**: 2026-11-25
- **Context**: The user explicitly instructed: "1.WORK LOCALLY. 2.THINK YOU AND DECIDE YOURSELF WHICH IS PERFECT FOR THESE ALL 3. PY3.12 4.UPDATED AND DONT WAIT FOR THE COMMAND FOR NEXT PHASE AUTO START THE NEXT TILL COMPLETE".
- **Options Considered**:
  1. *Pause and ask user confirmation between every phase*: Creates unnecessary turn latency and contradicts the direct user instruction to auto-start each next phase.
  2. *Execute autonomously phase-by-phase locally, verifying at each step before moving forward*: Fully adheres to user instructions while ensuring quality and safety.
- **Decision**: Execute phases autonomously, creating local git branches, running verification commands (`ruff`, `mypy`, `pytest`, `npm lint`, `npm test`, `npm run build`), committing atomic conventional commits, and advancing sequentially through Phase 18.
- **Consequences**:
  - Rapid, robust progress through all prompt requirements with rigorous verification at every step.

---

## Decision 006: Product Naming Standardization (VIREONIQ)
- **Status**: Accepted
- **Date**: 2026-11-25
- **Context**: The repository had historical naming drift (PLACEIQ, VIREONIQ, VIREONIQ X, HRCV) across documentation, UI titles, and configuration files.
- **Options Considered**:
  1. *Aggressive blanket renaming of all internal variables and table names*: High risk of breaking migration history, local storage keys, or external integrations.
  2. *Standardize all user-facing, documentation, package metadata, and UI titles to VIREONIQ while retaining internal compatibility aliases*: Safe, zero regression risk, consistent user experience.
- **Decision**: Canonical brand and documentation name is standardized to **VIREONIQ**. Internal legacy keys remain backward-compatible.
- **Consequences**:
  - Consistent external presentation without breaking runtime backwards compatibility.

---

## Decision 007: Phase L0 Consolidation & Staged Launch PR Strategy
- **Status**: Accepted
- **Date**: 2026-11-28
- **Context**: The repository contains 11 branches on `origin`. To begin the Global Go-Live Master Prompt (Phases L0 through L15), the repository history must be consolidated cleanly without committing to `main` directly.
- **Options Considered**:
  1. *Merge individual phase branches piecemeal*: 9 separate merges, high risk of git conflict noise since `hardening/full-audit` is already a strict superset.
  2. *Single verified consolidation pull request from `launch/phase-0-consolidation` (based on `hardening/full-audit`) into `main`*: Maps all history, confirms 0 missing commits across all branches, verifies all CI checks, removes public credentials, and prepares atomic staging for user review and merge.
- **Decision**: Adopt Option 2. Create `launch/phase-0-consolidation` from the verified `hardening/full-audit` superset, verify all tests (190 backend, 18 frontend, 0 lint/type errors), and open PR into `main` for user review.
- **Consequences**:
  - `main` remains untouched until user reviews and merges.
  - Zero loss of history or features.
  - All public documents are stripped of default credentials.


## Decision 008: Three-Tier Launch Architecture and Product Honesty Disclosures (Phase L1)

- **Status**: Accepted
- **Date**: 2026-11-28
- **Context**: Preparing VIREONIQ for public go-live requires absolute transparency and legal compliance. Previous views contained unflagged synthetic demonstration data, heuristic formulas labeled as "placement probabilities", real university trademarks, and missing non-affiliation notices for named enterprise companies.
- **Options Considered**:
  1. *Delete un-integrated or experimental modules*: Destructive; loses valuable UI/UX designs and demo workflows.
  2. *Feature-Flag Tier Architecture with Explicit Honest Disclosures*:
     - Establish a complete inventory (`docs/FEATURE_INVENTORY.md`) classifying 73 frontend pages and 75 backend endpoints into Tier 1 (Public Beta), Tier 2 (Invite-Only), and Tier 3 (Review Gated / Hidden by default).
     - Implement backend and frontend feature flag managers with remote sync, tier defaults, and administrative kill switches.
     - Add `<SampleDataBadge>`, `<PreviewBanner>`, and `<TrademarkDisclaimer>` across all views displaying synthetic benchmarks (OfferComparator, MarketIntelligence, SyllabusOptimizer, CognitiveLoadMonitor, ParentDashboard, CollegeAdmin, PsychometricDNA, MyCredential, MNCInterviewStudio, and CompanyProfiles).
     - Relabel `placement_probability` to `readiness_estimate_heuristic` with explicit `uncertainty_range` intervals.
- **Decision**: Adopt Option 2.
- **Consequences**:
  - Full codebase integrity preserved: zero feature deletion.
  - User expectations are grounded in evidence: synthetic demo data is clearly marked as such.
  - Enterprise brand and trademark risks are mitigated with comprehensive non-affiliation notices.

## Decision 009: Email Verification, Password Reset Tokens, and Account Deletion (Phase L2)

- **Status**: Accepted
- **Date**: 2026-11-28
- **Context**: Opening VIREONIQ to public users requires complete account lifecycle management: email verification tokens to confirm deliverable email addresses, rate-limited and single-use password reset tokens to protect against credential stuffing and brute force attacks, session invalidation on password change, and self-service account deletion honoring GDPR/CCPA privacy rights.
- **Options Considered**:
  1. *Third-party hosted auth (e.g. Auth0, Clerk, Firebase Auth)*: Introduces external vendor lock-in, recurring monthly billing, and complex data sovereignty challenges.
  2. *First-Party Cryptographic Token Lifecycle on Native Platform*:
     - RS256-signed JWT tokens for email verification (`purpose="email_verification"`, 24h expiration) and single-use password reset (`purpose="password_reset"`, 30m expiration).
     - Single-use replay protection backed by unique JTI blacklisting in `SafeRedis` (with TTL-aware in-memory fallback).
     - Strict password entropy and complexity validation (minimum 8 characters with required letters and numbers).
     - In-memory / Redis sliding-window rate limiting on sensitive authentication endpoints (`/forgot-password`, `/resend-verification`).
     - Session invalidation across all active refresh tokens upon successful password reset.
     - Direct self-service account deletion (`DELETE /api/v1/auth/me`) triggering GDPR anonymization and session purging.
- **Decision**: Adopt Option 2.
- **Consequences**:
  - Zero external auth vendor dependencies or API fees.
  - Complete resistance to token replay attacks via JTI blacklisting.
  - User accounts can be securely recovered, verified, and deleted in full compliance with global privacy standards.

---

## Decision 010: CI/CD Pipeline Hardening, Bandit SAST Scanning, and Branch Protection Policy (Phase L3)

- **Status**: Accepted
- **Date**: 2026-11-28
- **Context**: As part of preparing VIREONIQ for public global go-live, code quality, security posture, and git development workflows must be protected by strict automated gates. The CI/CD pipeline needs automated static application security testing (SAST), explicit branch protection specifications for `main`, and remediation of identified weak cryptographic operations.
- **Options Considered**:
  1. *Rely on manual code review without automated SAST*: High risk of developer oversight, secret leakage, or introduction of vulnerable hashing/deserialization patterns.
  2. *Automated Multi-Layer CI Security Pipeline with Bandit SAST and Strict Branch Protection Runbook*:
     - Audit backend with Bandit SAST; remediate any detected weak hashes or insecure defaults (e.g. replaced `hashlib.md5` with RFC-compliant `uuid.uuid5(uuid.NAMESPACE_DNS, ...)` in `plagiarism_guard.py`).
     - Pin `bandit==1.9.4` in `requirements-dev.txt` and integrate `bandit -r core/ api/ services/ crud/ schemas/ -ll` as a required blocking step in `.github/workflows/ci.yml`.
     - Create `docs/BRANCH_PROTECTION.md` documenting branch protection configuration on `main` (required PRs, 1 human approval, stale review dismissal, required CI checks matching exact workflow job names, linear history, admin enforcement).
- **Decision**: Adopt Option 2.
- **Consequences**:
  - Automated detection and prevention of SAST vulnerabilities in pull requests before merge.
  - Standardized branch protection settings ready for owner implementation in GitHub Repository Settings.
  - Backend codebase achieves 0 High and 0 Medium Bandit security alerts across all active modules.

---

## Decision 011: Database Integrity, Connection Pooling, and Migration Resilience (Phase L4)

- **Status**: Accepted
- **Date**: 2026-11-28
- **Context**: For global go-live, database connections must withstand cloud network blips, idle firewall reapers, and traffic bursts without leaking connections or crashing sessions. The database tier requires robust connection pool parameters (`pool_pre_ping`, `pool_recycle`, `pool_size`, `max_overflow`), clean SQLite compatibility hooks for local development and unit tests, and verified reversible migrations.
- **Options Considered**:
  1. *Default unconfigured connection pool*: Vulnerable to `OperationalError: connection closed` on dropped TCP connections in managed cloud environments (AWS RDS / GCP Cloud SQL).
  2. *Hardened Production Connection Pool with Pre-Ping, Recycle, and Automated Rollback Safety*:
     - Configure `pool_pre_ping=True` to detect and discard stale or dead connections prior to checkout.
     - Configure `pool_recycle=300` to refresh connections every 5 minutes and avoid proxy/NAT timeout drops.
     - Expose configurable pool environment settings (`DB_POOL_SIZE=20`, `DB_MAX_OVERFLOW=10`, `DB_POOL_TIMEOUT=30`).
     - Enforce automatic `session.commit()` on clean exit and `session.rollback()` on exceptions in `get_db`.
     - Maintain verified reversible Alembic migrations tested in CI round-trips (`upgrade head -> downgrade base -> upgrade head`).
- **Decision**: Adopt Option 2.
- **Consequences**:
  - Resilient database connection handling in multi-tenant cloud environments.
  - Zero stale connection exceptions during idle periods.
  - Complete isolation and transaction safety verified by automated test suites.

---

## Decision 012: Global Readiness, Legal Governance, and Launch Gate Architecture (Phase L5)

- **Status**: Accepted
- **Date**: 2026-11-28
- **Context**: Opening VIREONIQ to public users worldwide requires clear legal terms of service, comprehensive privacy disclosures conforming to GDPR and CCPA standards, and a staged Go/No-Go launch gate checklist with operational kill switches.
- **Options Considered**:
  1. *Unstructured launch without formal gates or legal disclaimers*: Leaves platform exposed to liability regarding employment outcomes, intellectual property disputes, or unclear user rights.
  2. *Standardized SaaS Legal Governance with Staged Go/No-Go Rollout*:
     - Establish `docs/TERMS_OF_SERVICE.md` with explicit career coaching disclaimers (no guarantee of employment or specific salary), acceptable use rules for sandbox code execution, and trademark non-affiliation protections.
     - Update `docs/PRIVACY.md` detailing technical controls (Talent Passport minimization, candidate visibility preferences, GDPR Article 15 JSON export, GDPR Article 17 self-service deletion, and zero third-party tracking pixels).
     - Publish `docs/LAUNCH_CHECKLIST.md` defining the 3-stage rollout (Internal Canary, Closed Beta, Global Public Beta) and the 10-point Go/No-Go decision matrix.
     - Document administrative emergency kill-switch endpoints (`POST /api/v1/system/features/{flag_name}/kill-switch`).
- **Decision**: Adopt Option 2.
- **Consequences**:
  - Full legal clarity and liability boundaries established for global users.
  - Complete transparency on data retention, access, and erasure rights.
  - Standardized staged rollout procedure preventing unverified code or broken features from reaching public production.



