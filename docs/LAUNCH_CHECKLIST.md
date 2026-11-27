# VIREONIQ — Global Launch Readiness & Go/No-Go Checklist

This runbook defines the staged rollout strategy, verification gates, and Go/No-Go decision criteria for opening VIREONIQ to public users worldwide.

---

## 1. Staged Rollout Strategy

```
┌─────────────────────────────────┐
│     Stage 1: Internal Canary    │  --> Maintainers & core team (production canary smoke tests)
└────────────────┬────────────────┘
                 ▼
┌─────────────────────────────────┐
│    Stage 2: Closed Beta Gate    │  --> Invite-only access (universities, partner colleges, pilot cohorts)
└────────────────┬────────────────┘
                 ▼
┌─────────────────────────────────┐
│    Stage 3: Global Public Beta  │  --> Full public registration with Tier 1 features active
└─────────────────────────────────┘
```

### Stage 1: Internal Canary (Smoke Verification)
- Deploy to isolated production environment.
- Run automated synthetic smoke tests:
  - User registration -> email verification token receipt -> successful login.
  - Resume upload -> parsing -> heuristic analysis.
  - Coding question execution -> sandboxed evaluation via Judge0.
  - Password reset cycle -> JTI blacklist replay verification.
  - Account deletion (`DELETE /api/v1/auth/me`) -> database cascade verification.

### Stage 2: Closed Beta / Invite-Only
- Enable registration strictly via invite code or domain whitelist (e.g., accredited partner colleges).
- Tier 1 and Tier 2 features active for approved cohorts.
- Close monitoring of Sentry error rates, Redis memory utilization, and PostgreSQL connection pool saturation.

### Stage 3: Global Public Beta
- Open self-registration to public users worldwide.
- Tier 1 features enabled globally by default.
- Tier 2 (advanced enterprise recruiting) and Tier 3 (experimental / un-integrated) remain feature-flagged.

---

## 2. Go / No-Go Decision Gate Matrix

Every gate must reach **GO** status prior to public traffic routing:

| Gate # | Area | Verification Standard | Current Status | Evidence / Verification |
| :---: | :--- | :--- | :---: | :--- |
| **G1** | **CI/CD Pipeline** | 100% green on GitHub Actions default branch pipeline. | **GO** | Runs `#46063760452`, `#46069296997`, `#46070762001`, `#46072003805`, `#46072970291` passing. |
| **G2** | **Static Security (SAST)** | 0 High and 0 Medium Bandit security vulnerabilities across all backend code. | **GO** | Bandit SAST scanned 36,531 lines: 0 issues identified. |
| **G3** | **Secret Hygiene** | 0 hardcoded AWS, OpenAI, GitHub, or private SSH keys tracked in git. | **GO** | Automated CI secret regex scanner passed across all tracked files. |
| **G4** | **Database & Migrations** | Round-trip migrations (`upgrade head -> downgrade base -> upgrade head`) passing. | **GO** | Verified in CI on live PostgreSQL 16 container. |
| **G5** | **Connection Pooling** | `pool_pre_ping=True`, `pool_recycle=300`, session rollback on exception. | **GO** | Verified in `test_database_integrity.py` (5 passed). |
| **G6** | **Account Lifecycle** | RS256 email verification, single-use password reset with Redis JTI blacklist, account deletion. | **GO** | Verified in `test_auth_lifecycle.py` (5 passed). |
| **G7** | **Product Honesty** | All synthetic benchmarks labeled with `<SampleDataBadge>`; trademark non-affiliation notices visible. | **GO** | Verified in `test_product_honesty.py` and `productHonesty.test.tsx`. |
| **G8** | **Feature Tiers** | Enterprise feature flag manager defaults experimental/un-integrated pages to hidden. | **GO** | Verified in `test_feature_flags.py` and `docs/FEATURE_INVENTORY.md`. |
| **G9** | **Legal & Privacy** | Terms of Service, Privacy Policy, GDPR deletion and export endpoints implemented. | **GO** | `docs/TERMS_OF_SERVICE.md`, `docs/PRIVACY.md`, `DELETE /api/v1/auth/me`. |
| **G10** | **Frontend Production** | 0 ESLint errors, strict TypeScript compilation (`tsc --noEmit`), production Vite build. | **GO** | 22 Vitest tests passing; clean Vite production bundle generated. |

---

## 3. Operational Kill Switches & Emergency Procedures

1. **Traffic Kill Switch**:
   - In the event of a critical security disclosure or severe data corruption, set `FEATURE_PLATFORM_MAINTENANCE_MODE=true` in environment configuration to gracefully route users to a maintenance screen while preserving database integrity.
2. **Feature Kill Switches**:
   - Administrative endpoint: `POST /api/v1/system/features/{flag_name}/kill-switch?enabled=false` instantly disables any individual feature without requiring a service redeploy.
3. **Database Incident Recovery**:
   - Immediate rollback: `alembic downgrade -1` (tested reversible downgrade scripts).
   - Point-in-time recovery runbook: refer to `docs/OPERATIONS.md`.
