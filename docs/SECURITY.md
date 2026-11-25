# VIREONIQ Security Architecture & Hardening Controls

## 1. Authentication, Sessions & Access Control

- **Password Hashing**: Argon2id via `passlib==1.7.4` + `argon2-cffi==25.1.0` (`backend/core/security.py`). Unusable account markers (`!`-prefixed hashes) fail verification cleanly without raising 500 errors.
- **JWT Asymmetric Tokens**: RS256 signed JWTs (`ACCESS_TOKEN_EXPIRE_MINUTES=15`, `REFRESH_TOKEN_EXPIRE_DAYS=7`) with lazy key initialization, Redis `blacklist:{jti}` access revocation, and DB-backed refresh token rotation (`POST /api/v1/auth/refresh`, `HttpOnly`, `SameSite=Lax`, `Secure` in production).
- **Registration & RBAC**: Public self-registration (`POST /api/v1/auth/register`) restricts `role_name` to standard candidate/user roles (`User`, `student`, `candidate`) and rejects elevated roles (`Admin`, `Recruiter`, `Faculty`) with HTTP 403. Case-insensitive RBAC dependencies (`require_roles`) guard recruiter, workforce, and faculty routes.
- **AI Orchestration RBAC**: `POST /api/v1/ai/tasks/execute` (`endpoints/ai_orchestration.py`) ignores client-supplied role overrides and resolves permissions strictly from `current_user.role`.
- **WebSocket Authentication**: `/api/v1/ws/matchmaker/{user_id}` and `/api/v1/advanced/adversarial/{session_id}/stream` verify JWT access tokens and session/user ownership prior to `websocket.accept()`.

## 2. Production Configuration Guardrails

At application startup (`backend/main.py` lifespan -> `Settings.validate_production_settings()` in `backend/core/config.py`), `ENVIRONMENT=production` fails closed if any of the following occur:
- `SECRET_KEY` or `CREDENTIAL_SIGNING_KEY` uses the insecure default value or is shorter than 32 characters.
- `DATABASE_URL` or `POSTGRES_PASSWORD` uses SQLite or the default `password` value (no silent SQLite auto-failover in production).
- `BACKEND_CORS_ORIGINS` contains wildcard `"*"` while `allow_credentials=True`.
- RSA keys are absent (neither `JWT_PRIVATE_KEY`/`JWT_PUBLIC_KEY` env vars nor PEM files at `PRIVATE_KEY_PATH` / `JWT_PRIVATE_KEY_PATH`).

Demo seed scripts (`backend/scripts/seed_user.py`, `seed_demo_data.py`, `seed_resilience_demo.py`, `init_db_schema.py`) explicitly refuse to run when `is_production` is true. Dev offline mock auth (`frontend/src/lib/mockAuth.ts`) is strictly gated behind `import.meta.env.DEV && VITE_ENABLE_MOCK_AUTH === 'true'`.

## 3. Tenant Isolation, Payments & Sandboxing

- **Multi-Tenant Isolation**:
  - `GET /api/v1/privacy-security/audit-logs` filters `SecurityAuditLog.actor_id == current_user.id` for non-admin callers.
  - `/api/v1/platform/api-keys*`, `/webhooks`, and `/connectors` enforce `tenant_id` ownership.
  - `/uploads/offline-bundles` is the only static upload mount; private candidate resume uploads are not served statically without auth.
- **Payment Verification**: `POST /api/v1/payments/verify` fails closed (HTTP 503) if `RAZORPAY_KEY_SECRET` is unconfigured and validates HMAC-SHA256 signature, transaction owner (`tx.user_id == current_user.id`), pending status (409 on replay), and exact plan amount.
- **Credential Minting**: `evaluate_and_issue_credential` refuses to issue signed credentials when no `SkillEvidence` exists (`NOT_ELIGIBLE`) and signs payloads with `CREDENTIAL_SIGNING_KEY` + constant-time `hmac.compare_digest`.
- **Code Execution Sandbox**: Host execution via `sys.executable -c` and synthetic passing test fabrication in `judge0_provider.py` and `code_execution_service.py` were removed; requests fail closed with explicit `Sandbox Unavailable` (`status.id = 13`, `passed = False`) when `JUDGE0_API_URL` is unconfigured or unreachable.

## 4. Known Dependency Advisories & Pending Governance Decisions

- **`python-jose` (`3.5.0`)**: Upgraded from `3.3.0` to `3.5.0`; `PYSEC-2026-4298` remains open upstream. Replacing `python-jose` with `pyjwt[cryptography]` and `passlib==1.7.4` (unmaintained) with `pwdlib[argon2]` / `argon2-cffi` requires explicit maintainer sign-off.
- **Frontend Runtime npm Advisories**: `npm audit --omit=dev` flags 5 advisories across `jspdf@^2.5.1` (0 direct imports in `frontend/src/`), transitive `dompurify`, `react-router-dom@^6.22.0`, transitive `react-router`, and `zod@^3.22.4`. All available fixes require semver-major upgrades (`jspdf@4.2.1`, `react-router-dom@7.18.7`, `zod@4.6.7`).
- **Access Token Storage**: `backend/api/deps.py` (`OAuth2PasswordBearer`) reads `Authorization: Bearer` tokens rather than cookies; therefore `frontend/src/store/authStore.ts` persists the access token in Zustand (`vireoniq-auth`). Migrating API auth extraction to `HttpOnly` access cookies is tracked for future hardening.
