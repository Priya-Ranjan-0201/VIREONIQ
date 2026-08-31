# VIREONIQ X — Enterprise Security & Zero-Trust Governance

**Release**: `v16.0.0-rc1`  
**Security Standard**: Zero-Trust Architecture & Cryptographic Integrity

---

## 1. Authentication & Password Security

- **Password Hashing**: Cryptographic password storage using **Argon2id** (`passlib.handlers.argon2` with $m=65536, t=3, p=4$), designed to increase resistance to GPU/ASIC-assisted password cracking.
- **JWT Asymmetric Tokens**: API requests are authenticated using **RS256 asymmetric signing** (RSA 2048-bit keys) with token expiration and revocation tracking.
- **Role-Based Access Control (RBAC)**: Strict permission boundaries separating `candidate`, `recruiter`, `faculty`, `mentor`, and `admin` roles.

---

## 2. Multi-Tenant Isolation & IDOR Defense

- **Tenant Boundaries**: All organizational data (e.g. employee skills, candidates, jobs, analytics) is isolated by `organization_id` derived exclusively from authenticated user token claims.
- **IDOR Protection**: Direct database queries filter strictly on `user_id == current_user.id` or organizational scope; direct query parameter overrides are forbidden.

---

## 3. Cryptographic Credential Authentication & Integrity

- **HMAC-SHA256 Signatures**: Issued digital credentials compute **HMAC-SHA256 authenticated integrity protection** over a canonical, normalized payload:
  $$\text{Payload} = \text{cred\_id} \,\|\, \text{user\_ref} \,\|\, \text{competency} \,\|\, \text{level} \,\|\, \text{issuer} \,\|\, \text{issued\_at} \,\|\, \text{version}$$
- **Verification Engine**: Altered skill names, scores, or dates cause immediate verification failure without silent degradation.

---

## 4. Autonomy Level 3 Safety Guard

- **High-Impact Action Guard**: Autonomous workflows are governed by Autonomy Level 3 policies. High-impact operations (`APPLY_JOB`, `MESSAGE_RECRUITER`, `PUBLISH_CREDENTIAL`, `CHANGE_GOAL`) require explicit user confirmation (`is_confirmed=True`) before execution.
- **Unilateral Action Ban**: AI agents are strictly forbidden from independently hiring, rejecting, or submitting irreversible applications without candidate or recruiter sign-off.
