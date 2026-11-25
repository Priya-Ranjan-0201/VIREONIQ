# VIREONIQ Security Architecture & Hardening Controls

## 1. Authentication, Sessions & Access Control

- **Password Hashing**: Argon2id via `passlib` + `argon2-cffi` (`backend/core/security.py`). Unusable account markers (`!`-prefixed hashes) fail verification cleanly without raising 500 errors.
- **JWT Asymmetric Tokens**: RS256 signed JWTs (`ACCESS_TOKEN_EXPIRE_MINUTES=15`, `REFRESH_TOKEN_EXPIRE_DAYS=7`) with Redis `blacklist:{jti}` access revocation and DB-backed refresh token rotation (`POST /api/v1/auth/refresh`, `HttpOnly`, `SameSite=Lax`, `Secure` in production).
- **Registration & RBAC**: Public self-registration (`/api/v1/auth/register`) restricts `role_name` to standard candidate/user roles (`User`, `student`, `candidate`) and rejects elevated roles (`Admin`, `Recruiter`, `Faculty`) with HTTP 403. Case-insensitive RBAC dependencies (`require_roles`) guard recruiter, workforce, and faculty routes.
- **AI Orchestration RBAC**: `POST /api/v1/ai-orchestration/tasks/execute` ignores client-supplied role overrides and resolves role permissions strictly from `current_user.role`.
- **WebSocket Authentication**: `/ws/matchmaker/{user_id}` and `/adversarial/{session_id}/stream` verify JWT access tokens and session/user ownership prior to `websocket.accept()`.

## 2. Production Configuration Guardrails

At application startup (`backend/main.py` lifespan -> `Settings.validate_production_settings()` in `backend/core/config.py`), `ENVIRONMENT=production` fails closed if any of the following occur:
- `SECRET_KEY` or `CREDENTIAL_SIGNING_KEY` uses the insecure default value or is shorter than 32 characters.
- `DATABASE_URL` or `POSTGRES_PASSWORD` uses SQLite or the default `password` value (no silent SQLite auto-failover in production).
- `BACKEND_CORS_ORIGINS` contains wildcard `"*"` while `allow_credentials=True`.
- RSA keys are absent (neither `JWT_PRIVATE_KEY`/`JWT_PUBLIC_KEY` env vars nor PEM files at `PRIVATE_KEY_PATH` / `JWT_PRIVATE_KEY_PATH`).

Demo seed scripts (`backend/scripts/seed_user.py`, `seed_demo_data.py`, `seed_resilience_demo.py`, `init_db_schema.py`) explicitly refuse to run when `is_production` is true. Dev offline mock auth (`frontend/src/lib/mockAuth.ts`) is strictly gated behind `import.meta.env.DEV && VITE_ENABLE_MOCK_AUTH === 'true'`.

## 3. Tenant Isolation, Payments & Sandboxing

- **Multi-Tenant Isolation**:
  - `GET /privacy-security/audit-logs` filters `SecurityAuditLog.user_id == current_user.id` for non-admin callers.
  - `/platform/api-keys*`, `/platform/webhooks`, and `/platform/connectors` enforce `tenant_id` ownership.
  - `/uploads/offline-bundles` is the only static upload mount; private candidate resume uploads are not served statically without auth.
- **Payment Verification**: `POST /payments/verify` fails closed (HTTP 503) if `RAZORPAY_KEY_SECRET` is unconfigured and validates HMAC signature, transaction owner (`tx.user_id == current_user.id`), pending status, and exact plan amount.
- **Credential Minting**: `evaluate_and_issue_credential` refuses to issue signed credentials when no `SkillEvidence` exists (`NOT_ELIGIBLE`) and signs payloads with `CREDENTIAL_SIGNING_KEY` + constant-time `hmac.compare_digest`.
- **Code Execution Sandbox**: Host execution via `sys.executable -c` and synthetic passing test fabrication in `judge0_provider.py` and `code_execution_service.py` are removed; requests fail closed with explicit `Execution Sandbox Unavailable` status when `JUDGE0_API_URL` is unconfigured or unreachable.

## 4. Known Dependency Advisories & Pending Governance Decisions

- **`python-jose` (`3.5.0`)**: Upgraded from `3.3.0` (which carried 7 OSV advisories) to `3.5.0`; `GHSA-3qf3-8w2g-rqmx` / `PYSEC-2026-4298` remain open upstream. Replacing `python-jose` with `pyjwt[cryptography]` and `passlib` (unmaintained) with `pwdlib[argon2]` / direct `argon2-cffi` is flagged as an explicit architecture decision for the repository owner.
- **Access Token Storage**: Access tokens currently persist in browser `localStorage` (`vireoniq-auth`); migrating fully to HttpOnly cookies is tracked as a future security enhancement.
