# VIREONIQ Security Architecture & Hardening Controls

Every security control below maps directly to the implementing source module and its verifying test in `backend/tests/`.

---

## 1. Authentication, Sessions & Access Control

| Control | Implementation File | Verifying Test |
|---|---|---|
| **Argon2id Password Hashing** | `backend/core/security.py` | `test_security_hardening.py::test_verify_password_handles_unusable_markers` |
| **RS256 Asymmetric JWT** | `backend/core/security.py` | `test_security_hardening.py::test_production_settings_validation_rejects_defaults_and_reads_jwt_aliases` |
| **Refresh Token Rotation & Replay Block** | `backend/api/api_v1/endpoints/auth.py` | `test_security_hardening.py::test_auth_register_blocks_privilege_escalation_and_refresh_rotates` |
| **Privilege Escalation Guard on Signup** | `backend/api/api_v1/endpoints/auth.py` | `test_security_hardening.py::test_auth_register_blocks_privilege_escalation_and_refresh_rotates` |
| **Case-Insensitive RBAC (`require_roles`)** | `backend/api/deps.py` | `test_security_hardening.py::test_endpoint_rbac_and_tenant_isolation` |
| **AI Orchestration Role Spoofing Block** | `backend/api/api_v1/endpoints/ai_orchestration.py` | `test_security_hardening.py::test_endpoint_rbac_and_tenant_isolation` |
| **Authenticated WebSockets** | `backend/api/api_v1/endpoints/matchmaker.py`, `advanced_modes.py` | `test_security_endpoints_coverage.py::test_matchmaker_websocket_auth_and_ownership` |

---

## 2. Production Configuration & Environment Guardrails

At application startup (`backend/main.py` lifespan -> `Settings.validate_production_settings()` in `backend/core/config.py`), `ENVIRONMENT=production` fails closed with a `RuntimeError` if:
- `SECRET_KEY` or `CREDENTIAL_SIGNING_KEY` uses the insecure default value or is shorter than 32 characters.
- `DATABASE_URL` or `POSTGRES_PASSWORD` uses SQLite or the default `password` value (no silent SQLite auto-failover in production).
- `BACKEND_CORS_ORIGINS` contains wildcard `"*"` while `allow_credentials=True`.
- RSA keys are absent (neither `JWT_PRIVATE_KEY`/`JWT_PUBLIC_KEY` env vars nor PEM files at `PRIVATE_KEY_PATH` / `JWT_PRIVATE_KEY_PATH`).

**Demo Seed & Dev Guards**:
- Demo seed scripts (`backend/scripts/seed_user.py`, `seed_demo_data.py`, `seed_resilience_demo.py`, `init_db_schema.py`) explicitly refuse to execute when `is_production` is true.
- Dev offline mock auth (`frontend/src/lib/mockAuth.ts`) is strictly gated behind `import.meta.env.DEV && VITE_ENABLE_MOCK_AUTH === 'true'`.

---

## 3. Tenant Isolation, Payments & Sandboxing

| Control | Implementation File | Verifying Test |
|---|---|---|
| **Audit Log Scoping (Actor Isolation)** | `backend/api/api_v1/endpoints/privacy_security.py` | `test_security_hardening.py::test_endpoint_rbac_and_tenant_isolation` |
| **Platform API Key Tenant Isolation** | `backend/api/api_v1/endpoints/platform_developer.py` | `test_security_hardening.py::test_endpoint_rbac_and_tenant_isolation` |
| **Recruiter Discovery Privacy Flag** | `backend/crud/crud_user.py` | `test_security_hardening.py::test_sandbox_and_credential_fail_closed_and_search_respects_privacy` |
| **Fail-Closed Payment HMAC Verification** | `backend/api/api_v1/endpoints/payments.py` | `test_security_hardening.py::test_payments_verify_fails_closed_without_secret_and_validates_owner` |
| **Fail-Closed Credential Minting** | `backend/services/credential_issuance_service.py` | `test_security_hardening.py::test_sandbox_and_credential_fail_closed_and_search_respects_privacy` |
| **Judge0 Offline Execution Fail-Closed** | `backend/services/code/judge0_provider.py` | `test_security_hardening.py::test_sandbox_and_credential_fail_closed_and_search_respects_privacy` |

---

## 4. Model Supply Chain & Serialization Security

- **Safe Formats**: Only safe serialization formats (`.safetensors`, `.onnx`, `.json`, `.tflite`) are permitted for machine learning artifacts (`backend/core/model_safety.py`).
- **Forbidden Execution Formats**: Unsafe formats (`.pkl`, `.pickle`, `.joblib`, `.pt`, `.bin`) are explicitly forbidden and raise `ModelSecurityError`.
- **Integrity Pinning**: Model artifacts are validated against SHA-256 digests in `ModelIntegrityRegistry`. Unpinned or tampered artifacts are rejected at load time.
- **Verifying Test**: `backend/tests/test_security_hardening.py::test_model_supply_chain_security`.

---

## 5. Input Validation & MIME Magic-Byte Checks

- **MIME Magic-Byte Detection**: `backend/services/resume_service.py` and `backend/api/api_v1/endpoints/syllabus.py` inspect file content bytes via `python-magic` (`magic.from_buffer`), ensuring files disguised as PDFs or DOCX with text or executable payloads are rejected with HTTP 400.
- **Path Traversal Sanitization**: Upload filenames are passed through `os.path.basename` before filesystem writing to prevent directory traversal.
- **Verifying Test**: `backend/tests/test_security_hardening.py::test_upload_magic_byte_validation_rejects_spoofed_files`.

---

## 6. Prompt Injection Defense Posture

> [!WARNING]
> **Prompt Injection Defense Limitations**: The legacy `check_prompt_injection` function in `backend/core/security.py` is an elementary heuristic keyword blocklist. It is **not** a comprehensive defense against indirect prompt injection, hidden text, or adversarial framing. Full defense is established in Phase 7 via:
> 1. Render-versus-extract structural discrepancy detection (identifying zero-width characters, white-on-white text, and microscopic fonts).
> 2. Strict instruction-data channel separation (enclosing untrusted candidate text within immutable inert XML delimiters that system prompts explicitly declare non-executable).

---

## 7. Known Dependency Advisories & Pending Decisions

- **`python-jose` (`3.5.0`)**: `PYSEC-2026-4298` remains open upstream. Replacing `python-jose` with `pyjwt[cryptography]` and `passlib==1.7.4` with `pwdlib[argon2]` / `argon2-cffi` is queued pending maintainer sign-off.
- **Frontend Runtime npm Advisories**: Pinned in `docs/KNOWN_LIMITATIONS.md` pending semver-major review (`jspdf@4`, `react-router-dom@7`, `zod@4`).
- **Access Token Storage**: Currently held in Zustand memory (`vireoniq-auth`); migration to `HttpOnly` access cookies is queued.
