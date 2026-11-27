# VIREONIQ — Privacy & Data Protection Policy

**Last Updated**: November 2026  
**Status**: Production Launch Specification  

VIREONIQ is committed to respecting and protecting the privacy of our global users. This document details our data handling practices, technical privacy architecture, and user control mechanisms in alignment with global data protection standards (including the EU General Data Protection Regulation (GDPR) and the California Consumer Privacy Act (CCPA)).

---

## 1. Information We Collect

1. **Account Information**: Email address, hashed credentials (Argon2id), verification status, created timestamp, and authentication role (`candidate`, `student`, `recruiter`, `faculty`, `admin`).
2. **Candidate Profile & Career Data**: Name, target role, education details, skills, project links, resume text, and work experiences.
3. **Assessment & Practice Records**: Responses to coding challenges, interview audio/transcripts, question-level scores, rubric evaluations, and practice session timestamps.
4. **Technical & Audit Metadata**: Anonymized IP address, user agent, session identifiers, and security event logs (`SecurityAuditLog`) for fraud detection and system defense.

---

## 2. Technical Privacy Controls & Architecture

### 1. Talent Passport Minimization & Shared Links
- Candidate profiles and assessment evaluations remain protected behind authenticated routes with strict role-based access control (RBAC).
- When a candidate chooses to share their profile externally (`POST /api/v1/passport/share`), a cryptographically secure random share token is generated.
- The public view (`GET /api/v1/passport/public/{share_token}`) exposes only minimized, candidate-approved credentials (verified skills and badges), suppressing contact details, interview audio, and internal notes.

### 2. Candidate Visibility Preferences
Candidates maintain granular control over their profile discoverability via `GET /api/v1/privacy-security/preferences` and `PUT /api/v1/privacy-security/preferences`:
- `recruiter_discoverable`: Toggle whether verified recruiters can find the candidate in search queries.
- `public_passport_enabled`: Enable or disable public link access.
- `allow_assessment_sharing`: Control whether assessment badges are displayed to potential employers.
- `opt_in_demographic_auditing`: Independent opt-in for participating in aggregated fairness benchmarks.

### 3. Data Export (GDPR Article 15 — Right of Access)
- Authenticated candidates can trigger a full structured export of their personal data via `GET /api/v1/privacy-security/export`.
- Returns a standardized JSON archive containing profile data, verified skills, project evidence, simulation records, and activity summaries.
- Sensitive security credentials (password hashes, refresh token secrets) are strictly excluded from exports.

### 4. Account Deletion & Right to Erasure (GDPR Article 17)
- Candidates can exercise their right to erasure at any time via:
  - `DELETE /api/v1/auth/me` (First-party auth lifecycle endpoint)
  - `POST /api/v1/privacy-security/account/delete`
- **Cascading Data Purge**:
  - Automatically deletes `User`, `Profile`, `CandidatePrivacyPreference`, `SkillEvidence`, `ProjectEvidence`, and associated sessions.
  - Active JWT refresh tokens are immediately revoked and blacklisted.
- **Audit Anonymization**:
  - Security audit logs (`SecurityAuditLog`) retained for compliance and anti-fraud monitoring are irreversibly anonymized (e.g., `user_id` is disassociated and email is hashed to `deleted_<prefix>@anonymized.local`).

---

## 3. Data Retention & Third-Party Service Boundaries

| Service / Provider | Purpose | Data Transferred | Retention Policy |
| :--- | :--- | :--- | :--- |
| **PostgreSQL Database** | Core transactional store | Profile, assessments, credentials | Deleted upon account erasure request |
| **Redis Cache** | Session state, rate limits, token blacklist | Ephemeral tokens, JTIs, IP rate counters | TTL-bounded (15 min – 7 days auto-expiry) |
| **Judge0 Sandbox** | Code execution sandbox | Ephemeral student code submissions | Execution only; zero persistent storage |
| **AI LLM Gateway** | Text coaching, interview feedback | Prompt text, answer transcripts | Processed in-flight; no training on user PII |

---

## 4. Cookies & Client-Side Storage Transparency

VIREONIQ uses client-side storage strictly for essential platform functionality:
- `vireoniq_token` / `auth_token`: Essential session authentication (HTTP-only cookies or encrypted local storage).
- `theme-preference`: User interface dark/light theme preference.
- `feature-flags`: Local cache of enabled platform feature flags.
- **Zero Third-Party Advertising Trackers**: VIREONIQ does not deploy third-party advertising cookies, ad networks, or cross-site tracking pixels.

---

## 5. Contact & Data Protection Inquiries

For data protection inquiries, data subject access requests (DSAR), or privacy questions, contact our Data Protection Office at: `privacy@vireoniq.com`.
