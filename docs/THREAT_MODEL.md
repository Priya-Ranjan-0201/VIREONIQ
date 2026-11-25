# VIREONIQ — Threat Model & Risk Register

## 1. Threat Modeling Methodology

VIREONIQ maps core application controls across **STRIDE** threat categories and tracks corresponding verification tests in `backend/tests/`.

---

## 2. Threat Vector Matrix & Verified Controls

| STRIDE Threat | Potential Impact | Architectural Control | Verification Test(s) |
|:---|:---|:---|:---|
| **Spoofing** | Impersonation or self-assigned Admin signup | Argon2id password verification (handling `!` unusable markers), RS256 JWTs, refresh rotation & blacklist, candidate-only registration role allowlist, WS JWT checks | `test_jwt_rs256_token_creation_and_decoding` (`test_auth_security.py`), `test_auth_register_blocks_privilege_escalation_and_refresh_rotates` (`test_security_hardening.py`), `test_auth_me_logout_and_role_dependencies` (`test_phase4_and_ws_coverage.py`) |
| **Tampering** | Forged credentials, tampered payments, or arbitrary RCE | HMAC-SHA256 verification on credentials & payments (fail-closed without secret, owner & amount validation); removal of host Python sandbox fallback | `test_payments_verify_fails_closed_without_secret_and_validates_owner` & `test_sandbox_and_credential_fail_closed_and_search_respects_privacy` (`test_security_hardening.py`), `test_payment_order_and_hmac_verification_lifecycle` (`test_phase4_and_ws_coverage.py`) |
| **Repudiation** | Unrecorded intelligence outputs or security actions | `IntelligenceReceipt` lineage & `SecurityAuditLog` event capture | `test_section_147_universal_intelligence_receipt_lineage` (`test_phase15_final_convergence.py`), `test_section_102_security_audit_logging` (`test_phase11_security_privacy.py`) |
| **Information Disclosure** | Cross-tenant data leaks (IDOR) or unscoped logs | Tenant/user scoping across recruiter, workforce, platform API keys, webhooks, and security audit logs | `test_endpoint_rbac_and_tenant_isolation` (`test_security_hardening.py`), `test_section_97_cross_tenant_isolation` (`test_phase11_security_privacy.py`) |
| **Denial of Service** | Unbounded cache growth or concurrency contention | `SafeRedis` TTL-bounded fallback + SlowAPI limiter + concurrency load benchmark | `test_safe_redis_ttl_and_cooldown_recovery` (`test_security_hardening.py`), `test_concurrency_load.py` (`-m benchmark`) |
| **Elevation of Privilege** | Candidate accessing admin/recruiter routes or AI role spoof | Case-insensitive `require_roles(...)` dependencies and server-side role resolution in `ai_orchestration` | `test_endpoint_rbac_and_tenant_isolation` (`test_security_hardening.py`), `test_auth_me_logout_and_role_dependencies` (`test_phase4_and_ws_coverage.py`) |
| **Autonomous Drift** | High-impact external actions without consent | Level 3 autonomy confirmation guard (`is_confirmed` check raising `PermissionError` -> HTTP 403) | `test_section_141_autonomy_level_3_safety_guard` (`test_phase14_autonomous_career_os.py`) |
