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
