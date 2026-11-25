# VIREONIQ — Privacy & Data Protection Controls

## 1. Scope & Legal Disclaimer

VIREONIQ implements technical privacy controls (preference toggles, JSON data export, and account deletion endpoints). **These codebase controls have not been independently audited or certified for GDPR, CCPA, or SOC2 legal compliance.**

---

## 2. Implemented Controls (`backend/api/api_v1/endpoints/privacy_security.py`)

### 1. Talent Passport Minimization
- Full candidate profile and assessment records stay behind authenticated routes.
- Public sharing (`POST /api/v1/passport/share` -> `GET /api/v1/passport/public/{share_token}`) exposes a minimized public credential view.

### 2. Candidate Visibility Preferences
- Candidates can inspect and toggle recruiter discovery, public passport exposure, assessment sharing, and demographic auditing opt-in via `GET /api/v1/privacy-security/preferences` and `PUT /api/v1/privacy-security/preferences`.

### 3. JSON Data Export
- `GET /api/v1/privacy-security/export` returns an authenticated JSON export containing:
  - `export_metadata` (`user_id`, timestamp, version)
  - `profile` (`first_name`, `last_name`, `target_role`)
  - `skills` (`SkillEvidence`), `projects` (`ProjectEvidence`), `credentials` (`VerifiedCredential`), and `simulations` (`CareerSimulation`)
  - Password hashes and internal tokens are excluded.

### 4. Account Deletion (`POST /api/v1/privacy-security/account/delete`)
- Explicitly deletes `Profile`, `CandidatePrivacyPreference`, `SkillEvidence`, and the `User` row (cascading dependent relational children defined with `CASCADE`) while preserving immutable `SecurityAuditLog` entries with anonymized event metadata (`deleted_<prefix>@anonymized.local`).
- External caches, backups, or asynchronous downstream stores require operational expiry/purge procedures (`docs/OPERATIONS.md`).
