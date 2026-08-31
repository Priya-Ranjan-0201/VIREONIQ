# VIREONIQ X — Privacy & Data Protection Specification

## 1. Compliance Baseline

VIREONIQ X implements comprehensive data protection controls in alignment with **GDPR (General Data Protection Regulation)**, **CCPA (California Consumer Privacy Act)**, and global privacy standards.

---

## 2. Privacy Principles & Implementation

### 1. Data Minimization & Talent Passport Isolation
- **Private Profile**: Contact information, sensitive identity details, full assessment history, and internal notes are stored securely behind authenticated endpoints.
- **Public Talent Passport**: Only explicitly minted credentials, verified skills, and aggregate readiness metrics are surfaced via data-minimized public links (`/api/v1/passport/share`).

### 2. Candidate Discovery Opt-In / Opt-Out
- Candidates maintain complete sovereign control over recruiter visibility.
- Candidates can toggle `is_searchable_by_recruiters = False` at any time to immediately withdraw their profile from all talent discovery queries.

### 3. Right to Data Portability (GDPR Art. 20)
- Candidates can request an instant machine-readable JSON export of their complete record (`GET /api/v1/privacy-security/export`) encompassing:
  - Account profile & credentials
  - Skill evidence graph & assessments
  - Interview transcripts & audit receipts

### 4. Right to Erasure / "Right to be Forgotten" (GDPR Art. 17)
- Executing `POST /api/v1/privacy-security/delete-account` triggers permanent, irreversible deletion across all relational databases, cache layers, and vector indices.
- External backups discard deleted identifiers upon rotation.
